from django.utils import timezone
import json

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages

from weasyprint import HTML

from admin_panel.models import Coupon, Address
from product_management.models import Product
from order_management.models import UserOrder
from user_management.forms import AddressForm
from .models import PaymentGateway, PaymentLogs, UserWishList
from .utils import calculate_sub_total_amount, create_user_order

import razorpay


# Create your views here.
def cart_list(request):
    """Cart Functionality"""
    try:
        applied_coupon = request.session.get("applied_coupon", None)
        if applied_coupon:
            # Remove the applied coupon from the session
            del request.session["applied_coupon"]
        total_amount = 0
        cart = request.session.get("cart", {})
        cart_products = []
        total_amount, cart_products = calculate_sub_total_amount(
            cart=cart, total_amount=total_amount
        )

        context = {
            "cart_products": cart_products,
            "total_amount": total_amount,
        }
        return render(request, "customer_portal/cart.html", context)
    except Exception as e:
        return HttpResponse(str(e))


def add_to_cart(request, product_id):
    """Add product to cart session."""
    try:
        # Retrieve quantity from POST request and validate
        quantity = int(request.POST.get("quantity", 0))
        if quantity <= 0:
            return JsonResponse({"status": "error", "msg": "Quantity is required."})

        # Get the current cart from the session
        cart = request.session.get("cart", {})
        product_id_str = str(product_id)
        current_quantity = cart.get(product_id_str, 0)

        product = Product.objects.get(id=product_id)

        if current_quantity + quantity > product.quantity:
            return JsonResponse(
                {
                    "status": "error",
                    "msg": "Not enough stock available.",
                }
            )

        # Check for quantity limits
        if quantity > 10 or current_quantity + quantity > 10:
            available_quantity = 10 - current_quantity
            return JsonResponse(
                {
                    "status": "error",
                    "msg": (
                        f"You can only add {available_quantity} more of this product to your cart."
                        if available_quantity > 0
                        else "You cannot purchase more than 10 quantity."
                    ),
                }
            )

        # Update cart and save to session
        cart[product_id_str] = current_quantity + quantity
        request.session["cart"] = cart

        # Calculate total items in the cart
        cart_item_count = sum(cart.values())

        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "msg": "Product added to cart successfully",
                "cart_item_count": cart_item_count,
            }
        )

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


def update_cart_product_quantity(request, product_id):
    """update cart"""
    try:
        if request.method == "POST":
            quantity = int(request.POST.get("quantity"))
            if quantity <= 0:
                return JsonResponse({"status": "error", "msg": "Quantity is required."})

            operation = request.POST.get("operation")
            cart = request.session.get("cart", {})
            product_id_str = str(product_id)
            product = Product.objects.get(id=product_id)

            if operation == "cart_quantity_up":
                # Check if adding the quantity exceeds stock
                new_quantity = cart.get(product_id_str, 0) + quantity
                if cart.get(product_id_str, 0) >= 10:
                    return JsonResponse(
                        {
                            "status": "error",
                            "msg": "You cannot purchase more than 10 quantity.",
                        }
                    )
                elif new_quantity > product.quantity:
                    return JsonResponse(
                        {"status": "error", "msg": "Not enough stock available."}
                    )
                response_message = "Quantity Increase successfully!"
                cart[product_id_str] = new_quantity

            elif operation == "cart_quantity_down":
                # Prevent quantity from going below 1
                new_quantity = cart.get(product_id_str, 0) - quantity
                if new_quantity < 1:
                    return JsonResponse(
                        {"status": "error", "msg": "Minimum quantity is 1."}
                    )
                cart[product_id_str] = new_quantity
                response_message = "Quantity Decrease successfully!"
            request.session["cart"] = cart

            sub_total_amount = 0
            # for product_id, quantity in cart.items():
            #     product = Product.objects.get(id=product_id)
            #     sub_total_amount += product.price * quantity

            sub_total_amount, _ = calculate_sub_total_amount(cart, sub_total_amount)

            # Retrieve applied coupon from the sessions
            total_amount = sub_total_amount
            discount_percent = 0
            discount_amount = 0
            coupon_code = ""
            applied_coupon = request.session.get("applied_coupon", None)

            if applied_coupon:
                coupon_code = applied_coupon["code"]
                discount_percent = applied_coupon["discount_percent"]
                discount_amount = (total_amount) * (discount_percent / 100)
                total_amount -= discount_amount
            return JsonResponse(
                {
                    "status": "success",
                    "cart": cart,
                    "sub_total_amount": sub_total_amount,
                    "total_amount": total_amount,
                    "discount_amount": discount_amount,
                    "discount_percent": discount_percent,
                    "coupon_code": coupon_code,
                    "operation": operation,
                    "cart_quantity": cart.get(product_id_str, 1),
                    "msg": response_message,
                }
            )

    except Exception as e:
        return HttpResponse(str(e))


def remove_cart_product(request, product_id):
    """remove cart"""
    try:
        cart = request.session.get("cart", {})
        product_id_str = str(product_id)
        del cart[product_id_str]
        request.session["cart"] = cart

        sub_total_amount = 0
        # for product_id, quantity in cart.items():
        #     product = Product.objects.get(id=product_id)
        #     sub_total_amount += product.price * quantity

        sub_total_amount, _ = calculate_sub_total_amount(cart, sub_total_amount)

        # Retrieve applied coupon from the sessions
        total_amount = sub_total_amount
        discount_percent = 0
        discount_amount = 0
        coupon_code = ""
        applied_coupon = request.session.get("applied_coupon", None)
        if applied_coupon:
            coupon_code = applied_coupon["code"]
            discount_percent = applied_coupon["discount_percent"]
            discount_amount = (total_amount) * (discount_percent / 100)
            total_amount -= discount_amount

        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "discount_percent": discount_percent,
                "sub_total_amount": sub_total_amount,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
                "coupon_code": coupon_code,
            }
        )
    except Exception as e:
        return HttpResponse(str(e))


def clear_cart(request):
    """clear cart"""
    try:
        if request.method == "POST":
            # Remove all items from the cart
            request.session["cart"] = {}
            return JsonResponse({"status": "success", "message": "Cart cleared"})
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )
    except Exception as e:
        return HttpResponse(str(e))


def apply_coupon(request):
    """apply coupon"""
    try:
        if request.method == "POST":
            coupon_code = request.POST.get("coupon_code")
            total_amount = float(request.POST.get("total_amount"))

            coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()

            if not coupon:
                return JsonResponse(
                    {"status": "error", "msg": "Invalid Coupon Code!"},
                    status=404,
                )
            if (
                not coupon.start_date < timezone.now()
                or not coupon.end_date > timezone.now()
            ):
                return JsonResponse(
                    {"status": "error", "msg": "Invalid Coupon Code!"},
                    status=404,
                )

            discount_percent = coupon.discount
            request.session["applied_coupon"] = {
                "code": coupon.code,
                "discount_percent": discount_percent,
            }
            if coupon_code == coupon.code:
                discount_amount = (total_amount) * (discount_percent / 100)
                new_total_amount = total_amount - discount_amount
                return JsonResponse(
                    {
                        "status": "success",
                        "discount_percent": discount_percent,
                        "discount_amount": discount_amount,
                        "new_total_amount": new_total_amount,
                    }
                )
            else:
                return JsonResponse(
                    {"status": "error", "message": "Invalid coupon code."}
                )

    except Exception as e:
        return HttpResponse(str(e))


def remove_coupon(request):
    try:
        applied_coupon = request.session.get("applied_coupon", None)
        if applied_coupon:
            # Remove the applied coupon from the session
            del request.session["applied_coupon"]

        cart = request.session.get("cart", {})
        sub_total_amount = 0
        # for product_id, quantity in cart.items():
        #     product = Product.objects.get(id=product_id)
        #     sub_total_amount += product.price * quantity

        sub_total_amount, _ = calculate_sub_total_amount(cart, sub_total_amount)

        total_amount = sub_total_amount
        discount_amount = 0
        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "sub_total_amount": sub_total_amount,
                "total_amount": total_amount,
                "discount_amount": discount_amount,
            }
        )

    except Exception as e:
        return HttpResponse(str(e))


# ----------------------------------------Wishlist-------------------------------------


@login_required(login_url="login_page")
def wishlist_list(request):
    """Cart Functionality"""
    try:
        wishlist_products = UserWishList.objects.filter(user=request.user)
        # Pagination
        paginator = Paginator(wishlist_products, 6)  # Show 10 orders per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "wishlist_item_count": page_obj.paginator.count,
        }
        return render(request, "customer_portal/wishlist.html", context)
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def add_to_wishlist(request, product_id):
    """Add product to cart session"""
    try:
        product = Product.objects.get(id=product_id)
        if not product:
            return JsonResponse(
                {"status": "error", "msg": "Invalid Product Id"}, status=400
            )
        wishlist, created = UserWishList.objects.get_or_create(
            user=request.user, product=product
        )
        # Calculate the number of items in the user's wishlist
        wishlist_item_count = UserWishList.objects.filter(user=request.user).count()
        if created:
            response_data = {
                "msg": "Product added to wishlist",
                "status": "success",
                "wishlist_item_count": wishlist_item_count,
            }
        else:
            response_data = {"msg": "Product already in wishlist", "status": "success"}
        return JsonResponse(response_data)
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def remove_wishlist_item(request, product_id):
    """remove item from wishlist"""
    if request.method == "POST":
        try:
            # Ensure the user is logged in
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"status": "error", "msg": "User not authenticated"}, status=401
                )

            # Find the wishlist item and delete it
            wishlist_item = UserWishList.objects.get(
                user=request.user, product_id=product_id
            )
            wishlist_item.delete()

            return JsonResponse(
                {"status": "success", "msg": "Item removed from wishlist"}
            )
        except UserWishList.DoesNotExist:
            return JsonResponse(
                {"status": "error", "msg": "Item not found in wishlist"}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})
    return JsonResponse(
        {"status": "error", "message": "Invalid request method"}, status=405
    )


@login_required(login_url="login_page")
def clear_wishlist(request):
    """clear wishlist"""
    try:
        if request.method == "POST":
            # Remove all wishlist items for the user
            UserWishList.objects.filter(user=request.user).delete()
            return JsonResponse({"status": "success", "message": "Wishlist cleared"})
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def checkout(request):
    try:
        sub_total_amount = 0
        cart = request.session.get("cart", {})
        cart_products = []

        addresses = Address.objects.filter(user=request.user, active=True).all()

        sub_total_amount, cart_products = calculate_sub_total_amount(
            cart, sub_total_amount
        )

        applied_coupon = request.session.get("applied_coupon", None)

        total_amount = sub_total_amount

        discount_amount = 0
        discount_percent = 0
        coupon_code = ""

        if applied_coupon:
            coupon_code = applied_coupon["code"]
            discount_percent = applied_coupon["discount_percent"]
            discount_amount = (total_amount) * (discount_percent / 100)
            total_amount -= discount_amount
        form = AddressForm()
        context = {
            "cart_products": cart_products,
            "sub_total_amount": sub_total_amount,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "coupon_code": coupon_code,
            "discount_percent": discount_percent,
            "addresses": addresses,
            "form": form,
        }

        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                address = form.save(commit=False)
                address.user = request.user
                address.created_by = request.user
                address.updated_by = request.user
                address.is_active = True
                address.save()

        return render(request, "customer_portal/checkout.html", context)
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def place_order(request):
    """Place order view"""
    try:
        if request.method == "POST":
            billing_address_id = request.POST.get("billing_address_id")
            shipping_address_id = request.POST.get("shipping_address_id")
            selected_payment = request.POST.get("selected_payment")

            cart = request.session.get("cart", {})
            sub_total_amount = 0
            sub_total_amount, _ = calculate_sub_total_amount(cart, sub_total_amount)

            if sub_total_amount <= 0:
                return JsonResponse({"status": "error", "msg": "Add Product first"})

            applied_coupon = request.session.get("applied_coupon", None)
            total_amount = sub_total_amount
            discount_amount = 0
            discount_percent = 0

            if applied_coupon:
                coupon_code = applied_coupon["code"]
                discount_percent = applied_coupon["discount_percent"]
                discount_amount = (total_amount) * (discount_percent / 100)
                total_amount -= discount_amount

            payment_response = dict()
            # Handle Razorpay payment
            if selected_payment == "payment_razorpay":
                # Create Razorpay client
                razorpay_client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )

                # Create an order in Razorpay
                razorpay_order = razorpay_client.order.create(
                    {
                        "amount": int(total_amount * 100),  # Amount in paisa
                        "currency": "INR",
                        "payment_capture": "1",
                    }
                )
                razorpay_order_id = razorpay_order["id"]

                payment_response = {
                    "status": "success",
                    "razorpay_order_id": razorpay_order_id,
                    "amount": total_amount,
                    "currency": "INR",
                    "key_id": settings.RAZORPAY_KEY_ID,
                }

                return JsonResponse(
                    payment_response
                )  # Return the Razorpay order ID to the frontend for payment processing

            else:
                applied_coupon = request.session.get("applied_coupon", None)
                if selected_payment == "payment_cash":
                    payment_gateway = PaymentGateway.objects.filter(
                        name="Cash On Delivery"
                    ).first()

                # Create UserOrder using the common function
                order = create_user_order(
                    user=request.user,
                    cart=cart,
                    billing_address_id=billing_address_id,
                    shipping_address_id=shipping_address_id,
                    applied_coupon=applied_coupon,
                    payment_gateway=payment_gateway,
                )

                # Clear the cart from session
                if cart:
                    del request.session["cart"]

                return JsonResponse(
                    {
                        "status": "success",
                        "msg": "Payment successful and order created",
                        "order_id": order.id,
                    }
                )

        else:
            return JsonResponse(
                {"status": "error", "msg": "Invalid request"}, status=400
            )

    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)}, status=500)


@csrf_exempt
def payment_handler(request):
    if request.method == "POST":
        try:
            billing_address_id = request.POST.get("billing_address_id")
            shipping_address_id = request.POST.get("shipping_address_id")
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            selected_payment = request.POST.get("selected_payment")

            user = request.user

            # Initialize Razorpay client
            razorpay_client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }

            # Verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)

            # If payment verification is successful, create the order in your local database
            cart = request.session.get("cart", {})
            applied_coupon = request.session.get("applied_coupon", None)
            if selected_payment == "payment_razorpay":
                payment_gateway = PaymentGateway.objects.filter(name="Razorpay").first()

            payment_status = "S"
            order = create_user_order(
                user,
                cart,
                billing_address_id,
                shipping_address_id,
                payment_gateway,
                payment_status,
                payment_id=payment_id,
                applied_coupon=applied_coupon,
                transaction_id=razorpay_order_id,
            )

            # Clear the cart from session
            if cart:
                del request.session["cart"]

            return JsonResponse(
                {
                    "status": "success",
                    "msg": "Payment successful and order created",
                    "order_id": order.id,
                }
            )

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse(
                {"status": "error", "msg": "Payment Failed Invalid signature"}
            )

        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})

    return HttpResponseBadRequest()


@csrf_exempt
def razorpay_webhook(request):
    """Handles webhook notifications from Razorpay."""
    response = json.loads(request.body.decode("utf8"))
    print("response: ", response)
    try:
        # Extract event and payload
        event = response.get("event", "")
        payload = response.get("payload", {})
        razorpay_order_id = (
            payload.get("payment", {}).get("entity", {}).get("order_id", "")
        )

        PaymentLogs.objects.create(
            pay_ord_id=razorpay_order_id,
            pay_status=event,
            response_dict=json.dumps(response),
        )

        return JsonResponse(
            {"status": "success", "msg": "Webhook processed successfully."}
        )
    except Exception as e:
        PaymentLogs.objects.create(
            pay_ord_id="",
            pay_status="Exception",
            response_dict=json.dumps({"response": response, "error": str(e)}),
        )
        return JsonResponse({"status": "error", "msg": str(e)}, status=500)


@login_required(login_url="login_page")
def order_successful(request, order_id):
    """order placed successfully"""
    try:
        order = UserOrder.objects.filter(id=order_id, user=request.user).first()
        discount_amount = order.get_sub_total() - float(order.grand_total)
        print("discount_amount: ", discount_amount)
        if order is None:
            return render(request, "customer_portal/order_not_found.html", {})
        return render(
            request,
            "customer_portal/order_successful.html",
            {
                "order": order,
                "discount_amount": discount_amount,
                "sub_total": order.get_sub_total(),
            },
        )
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.created_by = request.user
            address.updated_by = request.user
            address.is_active = True
            address.save()
            return JsonResponse({"status": "success"})
    else:
        form = AddressForm()

    return render(request, "customer_portal/add_address.html", {"form": form})


@login_required(login_url="login_page")
def order_pdf_view(request, order_id):
    """View to generate PDF for a specific order."""
    try:
        order = UserOrder.objects.get(id=order_id)
        discount_amount = float(order.get_sub_total()) - float(order.grand_total)
        print("discount_amount: ", discount_amount)

        # Render the HTML template
        template = get_template("customer_portal/order_pdf.html")
        html_content = template.render(
            {
                "order": order,
                "order_number": order.awb_no,
                "sub_total": order.get_sub_total(),
                "discount_amount": discount_amount,
                "order_total": float(order.grand_total),
                "user": request.user,
            }
        )

        # Generate PDF
        pdf_file = HTML(string=html_content).write_pdf()

        # Return PDF as response
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="order_{order.awb_no}.pdf"'
        )
        return response
    except UserOrder.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


@login_required(login_url="login_page")
def order_detail_view(request, order_id):
    order = get_object_or_404(UserOrder, id=order_id, user=request.user)
    discount_amount = order.get_sub_total() - float(order.grand_total)

    return render(
        request,
        "customer_portal/order_detail.html",
        {
            "order": order,
            "discount_amount": discount_amount,
            "sub_total": order.get_sub_total(),
        },
    )


@login_required(login_url="login_page")
def my_orders(request):
    """User orders"""
    orders = UserOrder.objects.filter(user=request.user).all()

    # Apply filters
    awb_no = request.GET.get("awb_no")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if awb_no:
        orders = orders.filter(awb_no=awb_no).order_by("-id")
    if status:
        orders = orders.filter(status=status).order_by("-id")

    if date_from and date_to:
        # Check date logic
        if date_from and date_to and date_from > date_to:
            messages.add_message(
                request, messages.ERROR, "End date must be after start date."
            )
            return redirect("my_orders")  # Redirect to the same or another view

        orders = orders.filter(created_at__range=[date_from, date_to])

    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "customer_portal/user_orders.html", {"page_obj": page_obj})


def track_order(request):
    """track order"""
    try:
        if request.method == "POST":
            awb_no = request.POST.get("awb_no")
            order = UserOrder.objects.filter(awb_no=awb_no).first()
            return render(request, "customer_portal/track_order.html", {"order": order})

        return render(request, "customer_portal/track_order.html")
    except Exception as e:
        return HttpResponse(str(e))
