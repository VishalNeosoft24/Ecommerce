from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path("cart/", views.cart_list, name="cart"),
    path("add-cart/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path(
        "update-cart/<int:product_id>",
        views.update_cart_product_quantity,
        name="update_cart",
    ),
    path(
        "remove-cart/<int:product_id>",
        views.remove_cart_product,
        name="remove_cart",
    ),
    # wishlist
    path("wishlist/", views.wishlist_list, name="wishlist"),
    path(
        "add-wishlist/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"
    ),
    path(
        "remove-wishlist-item/<int:product_id>/",
        views.remove_wishlist_item,
        name="remove_wishlist_item",
    ),
    # Coupon
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
]
