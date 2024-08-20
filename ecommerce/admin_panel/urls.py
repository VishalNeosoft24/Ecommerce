from django.urls import include, path
from . import views


urlpatterns = [
    # product_management_app
    path("", include("product_management.urls")),
    # users
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
    # Email Templates
    path(
        "email-templates/", views.list_all_email_templates, name="all_email_templates"
    ),
    path(
        "get-emailtemplates",
        views.get_all_email_templates,
        name="get_all_email_templates",
    ),
    path(
        "create-emailtemplate/",
        views.create_email_template,
        name="create_email_template",
    ),
    path(
        "update-emailtemplate/<int:id>/",
        views.update_email_template,
        name="update_email_template",
    ),
    path(
        "delete-emailtemplate/",
        views.delete_email_template,
        name="delete_email_template",
    ),
    # Banner
    path("banners/", views.list_all_banners, name="all_banners"),
    path("get-banners/", views.get_all_banners, name="get_all_banners"),
    path("create-banner/", views.create_banner, name="create_banner"),
    path("update-banner/<int:id>/", views.update_banner, name="upadte_banner"),
    path("delete-banner/", views.delete_banner, name="delete_banner"),
    # Flatpages
    path("flatpages/", views.flatpage_list, name="flatpage_list"),
    path("flatpages/create/", views.create_flatpage, name="create_flatpage"),
    path("flatpages/<int:pk>/edit/", views.update_flatpage, name="update_flatpage"),
    path("flatpages/<int:pk>/delete/", views.delete_flatpage, name="delete_flatpage"),
]
