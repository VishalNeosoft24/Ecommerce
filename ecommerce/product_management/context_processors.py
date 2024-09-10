import random

from django.shortcuts import get_object_or_404
from .models import Product, ProductImage
from django.db.models import Prefetch


def recommended_product(request):
    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "product_images",
                queryset=ProductImage.objects.filter(is_active=True)[:1],
                to_attr="first_image",
            )
        )
    )

    random_products = random.sample(list(products), min(len(products), 6))

    chunked_products = [
        random_products[i : i + 3] for i in range(0, len(random_products), 3)
    ]
    return {"chunked_products": chunked_products}
