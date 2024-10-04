from datetime import datetime

from admin_panel.utils import send_order_confirmation_email
from admin_panel.models import Coupon, Address, EmailTemplate
from product_management.models import Product
from order_management.models import UserOrder, OrderDetail


def calculate_sub_total_amount(cart, total_amount):
    """calculate subtotal"""
    cart_products = []
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_products.append({"product": product, "quantity": quantity})
        total_amount += product.price * quantity
    return total_amount, cart_products


def create_user_order(
    user,
    cart,
    billing_address_id,
    shipping_address_id,
    payment_gateway,
    payment_status="P",
    payment_id=None,
    applied_coupon=None,
    transaction_id=None,
):
    """Creates a UserOrder based on the given cart and addresses."""
    # Calculate subtotal from cart
    sub_total_amount, _ = calculate_sub_total_amount(cart, 0)

    # Initialize total_amount and discount details
    total_amount = sub_total_amount
    discount_amount = 0
    coupon = None
    # Check for applied coupon and calculate discount
    if applied_coupon:
        coupon_code = applied_coupon["code"]
        discount_percent = applied_coupon["discount_percent"]
        discount_amount = (total_amount) * (discount_percent / 100)
        total_amount -= discount_amount  # Update total_amount with discount
        coupon = Coupon.objects.filter(code=coupon_code).first()
        coupon.count = coupon.count + 1
        coupon.save()

    # Create UserOrder
    order = UserOrder(
        user=user,
        coupon=coupon,
        grand_total=total_amount,  # Store the discounted total
        billing_address=Address.objects.get(id=billing_address_id),
        shipping_address=Address.objects.get(id=shipping_address_id),
        transaction_id=transaction_id,
        payment_gateway=payment_gateway,
        payment_status=payment_status,
        payment_id=payment_id,
    )
    order.save()

    products = []
    # Create OrderDetail for each product in cart
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        order_detail = OrderDetail(
            order=order,
            product=product,
            amount=product.price * quantity,
            quantity=quantity,
        )
        order_detail.save()
        products.append(
            {
                "name": order_detail.product.name,
                "quantity": order_detail.quantity,
                "price": f"{order_detail.amount:.2f}",
            }
        )

    email_template_context = {
        "customer_name": order.user.get_full_name(),
        "order_number": order.awb_no,
        "order_date": order.created_at.strftime("%Y-%m-%d"),
        "order_total": order.grand_total,
        "products": products,
        "discount_amount": discount_amount,
        "current_year": datetime.now().year,
    }
    if coupon:
        email_template_context["coupon_code"] = coupon.code

    template = EmailTemplate.objects.filter(title="Order Confirmation").first()

    send_order_confirmation_email(user.email, email_template_context, template)

    return order
