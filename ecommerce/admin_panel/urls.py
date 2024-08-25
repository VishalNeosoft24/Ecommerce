from django.urls import path

from . import views


urlpatterns = [
    # users
    path("", views.home, name="admin-home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.create_user, name="register"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.all_users, name="users"),
    path("user/", views.update_user, name="update_user"),
    path("delete/", views.delete_user, name="delete_user"),
    # categories
    path("categories/", views.list_all_categories, name="all_categories"),
    path("get-categories/", views.get_all_categories, name="get_all_categories"),
    path("add-category/", views.add_category, name="add_category"),
    path("update-category/<int:id>/", views.update_category, name="update_category"),
    path("delete-category/", views.delete_category, name="delete_category"),
    # products
    path("products/", views.list_all_products, name="all_products"),
    path("get-products/", views.get_all_products, name="get_all_products"),
    path("add-product/", views.add_product, name="add_product"),
    path("file_upload_view/", views.file_upload_view, name="file_upload_view"),
    path("update-product/<int:id>/", views.update_product, name="update_product"),
    path("delete-product/", views.delete_product, name="delete_product"),
    # File Handling
    path("delete_file/", views.delete_file_view, name="delete_file"),
    path("delete_all_files/", views.delete_all_files_view, name="delete_all_files"),
    # Attributes
    path("handle-attributes/", views.handle_attributes, name="handle_attributes"),
    path("attributes/<int:id>/", views.update_attribute, name="update_attribute"),
    path(
        "delete-attributes/<int:attribute_id>/",
        views.delete_attribute,
        name="delete_attribute",
    ),
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
    path("flatpages/", views.flatpage_list, name="all_flatpages"),
    path("get-flatpages/", views.get_all_flatpage, name="get_all_flatpages"),
    path("flatpages/create/", views.create_flatpage, name="create_flatpage"),
    path(
        "flatpages/<int:flatpage_id>/edit/",
        views.update_flatpage,
        name="update_flatpage",
    ),
    path(
        "flatpages/<int:flatpage_id>/delete/",
        views.delete_flatpage,
        name="delete_flatpage",
    ),
    # orders
    path("orders/", views.list_all_orders, name="all_orders"),
    path("get-orders/", views.get_all_orders, name="get_all_orders"),
    path(
        "update-order/<int:order_id>/",
        views.update_order,
        name="update_order",
    ),
]
