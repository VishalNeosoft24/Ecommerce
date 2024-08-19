from django.urls import path
from . import views


urlpatterns = [
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
    # Attributes
    path("handle-attributes/", views.handle_attributes, name="handle_attributes"),
    path("attributes/<int:id>/", views.update_attribute, name="update_attribute"),
    path(
        "delete-attributes/<int:attribute_id>/",
        views.delete_attribute,
        name="delete_attribute",
    ),
]
