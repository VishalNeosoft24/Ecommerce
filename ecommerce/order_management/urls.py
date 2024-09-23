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
    path("clear-cart/", views.clear_cart, name="clear_cart"),
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
    path("clear-wishlist/", views.clear_wishlist, name="clear_wishlist"),
    # Coupon
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    # checkout
    path("checkout/", views.checkout, name="checkout"),
    # Place Order
    path("place-order/", views.place_order, name="place_order"),
    path(
        "order-successful/<int:order_id>/",
        views.order_successful,
        name="order_successful",
    ),
    path("add-address", views.add_address, name="add_address"),
    path("order/<int:order_id>/", views.order_pdf_view, name="order_pdf"),
    path("order-detail/<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("orders", views.my_orders, name="my_orders"),
    # payment
    path("paymenthandler/", views.paymenthandler, name="paymenthandler"),
]
