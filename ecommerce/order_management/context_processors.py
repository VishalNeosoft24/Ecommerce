from order_management.models import UserWishList


def cart_item_count(request):
    cart = request.session.get("cart", {})
    item_count = sum(cart.values())
    return {"cart_item_count": item_count}


def wishlist_item_count(request):
    if request.user.is_authenticated:
        wishlist_item_count = UserWishList.objects.filter(user=request.user).count()
    else:
        wishlist_item_count = 0
    return {"wishlist_item_count": wishlist_item_count}
