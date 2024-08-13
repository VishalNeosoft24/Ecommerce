from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="admin-home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.create_user, name="register"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.all_users, name="users"),
    path("user/", views.update_user, name="update_user"),
    path("delete/", views.delete_user, name="delete_user"),
    # coupons
    path("get-coupons/", views.get_all_coupons, name="get_all_coupons"),
    path("coupons/", views.list_all_coupons, name="all_coupons"),
    path("create-coupon/", views.create_coupon, name="create_coupon"),
    path(
        "get-coupon-details/<int:coupon_id>/",
        views.get_coupon_details,
        name="get_coupon_details",
    ),
    path("update-coupon/", views.update_coupon, name="update_coupon"),
    path("delete-coupon/", views.delete_coupon, name="delete_coupon"),
    # products
    path("products/", views.list_all_products, name="all_products"),
    path("get-products/", views.get_all_products, name="get_all_products"),
    path("add-product/", views.add_product, name="add_product"),
    path("file_upload_view/", views.file_upload_view, name="file_upload_view"),
    path("update-product/<int:id>/", views.update_product, name="update_product"),
    path("delete-product/", views.delete_product, name="delete_product"),
    # categories
    path("categories/", views.list_all_categories, name="all_categories"),
    path("get-categories/", views.get_all_categories, name="get_all_categories"),
    path("add-category/", views.add_category, name="add_category"),
    path("update-category/<int:id>/", views.update_category, name="update_category"),
    path("delete-category/", views.delete_category, name="delete_category"),
    # File Handling
    path("delete_file/", views.delete_file_view, name="delete_file"),
    path("delete_all_files/", views.delete_all_files_view, name="delete_all_files"),
    path("handle-attributes/", views.handle_attributes, name="handle_attributes"),
]
