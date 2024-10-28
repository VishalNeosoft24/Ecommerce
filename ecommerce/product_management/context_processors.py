import random

from admin_panel.models import UserEventTracking
from .models import Product, ProductImage, Category
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

    recommended_products = random.sample(list(products), min(len(products), 6))

    if request.user.is_authenticated:
        # Get the most recent events related to product views or other relevant events
        recent_events = UserEventTracking.objects.filter(
            user=request.user, event_type="product_view"
        ).order_by("-event_time")[:100]

        # Extract product_ids from the object_info
        product_ids = [
            event.object_info for event in recent_events if event.object_info
        ]
        if len(product_ids) > 3:
            # Fetch all products using a single query for the product_ids
            recommended_products = (
                Product.objects.filter(id__in=product_ids)
                .prefetch_related(
                    Prefetch(
                        "product_images",
                        queryset=ProductImage.objects.filter(is_active=True)[:1],
                        to_attr="first_image",
                    )
                )
                .distinct()
            )[:9]

    chunked_products = [
        recommended_products[i : i + 3] for i in range(0, len(recommended_products), 3)
    ]
    return {"chunked_products": chunked_products}


def categories_for_footer(request):
    footer_categories = Category.objects.filter(parent__isnull=True)[:5]
    return {"footer_categories": footer_categories}
