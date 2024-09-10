from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from product_management.models import Product
from .models import UserWishList
from admin_panel.models import Coupon


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
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            cart_products.append({"product": product, "quantity": quantity})
            total_amount += product.price * quantity
        context = {
            "cart_products": cart_products,
            "total_amount": total_amount,
        }
        return render(request, "customer_portal/cart.html", context)
    except Exception as e:
        return HttpResponse(str(e))


def add_to_cart(request, product_id):
    """Add product to cart session"""
    try:
        quantity = int(request.POST.get("quantity"))
        cart = request.session.get("cart", {})
        product_id_str = str(product_id)
        cart[product_id_str] = cart.get(product_id_str, 0) + quantity
        request.session["cart"] = cart
        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "msg": "Product Added to Cart Successfully",
            }
        )
    except Exception as e:
        return HttpResponse(str(e))


def update_cart_product_quantity(request, product_id):
    """update cart"""
    try:
        if request.method == "POST":
            quantity = int(request.POST.get("quantity"))
            operation = request.POST.get("operation")
            cart = request.session.get("cart", {})
            product_id_str = str(product_id)

            if operation == "cart_quantity_up":
                cart[product_id_str] = cart.get(product_id_str, 0) + quantity
            else:
                cart[product_id_str] = cart.get(product_id_str, 0) - quantity
            request.session["cart"] = cart

            sub_total_amount = 0
            for product_id, quantity in cart.items():
                product = Product.objects.get(id=product_id)
                sub_total_amount += product.price * quantity

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
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            sub_total_amount += product.price * quantity

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
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            sub_total_amount += product.price * quantity
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


def wishlist_list(request):
    """Cart Functionality"""
    try:
        wishlist_products = UserWishList.objects.filter(user=request.user)
        context = {"wishlist_products": wishlist_products}
        return render(request, "customer_portal/wishlist.html", context)
    except Exception as e:
        return HttpResponse(str(e))


def add_to_wishlist(request, product_id):
    """Add product to cart session"""
    try:
        product = Product.objects.get(id=product_id)
        if not product:
            return JsonResponse(
                {"status": "error", "msg": "Invalid Product Id"}, status=400
            )

        UserWishList.objects.get_or_create(user=request.user, product=product)
        return JsonResponse(
            {"status": "success", "msg": "Item Added to Wishlist Successfully"}
        )
    except Exception as e:
        return HttpResponse(str(e))


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
