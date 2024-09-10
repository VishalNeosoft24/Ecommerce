from django.urls import path
from . import views

urlpatterns = [
    # Product
    path("", views.home_page, name="home_page"),
    path(
        "fetch-products/",
        views.get_products_by_category,
        name="get_products_by_category",
    ),
    path("product-details/<int:id>", views.product_details, name="product_details"),
    path("products/", views.product_list, name="product_list"),
]
