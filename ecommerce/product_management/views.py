# Django imports
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.db.models import Prefetch, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Third-party and Python standard library imports
import random

# Local app imports
from admin_panel.views import fetch_sub_cat
from product_management.models import Product, ProductImage, Category
from admin_panel.models import Banner
from order_management.models import UserWishList


def home_page(request):
    """
    Renders the home page with featured products, categories, and banners.

    This view fetches:
    - Active products with their first image.
    - Categories with products, showing up to 6 categories, each with up to 4 products.
    - Banners that are active.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'index.html' template with categories, products, and banners.
    """

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

    categories_with_products = (
        Category.objects.annotate(product_count=Count("category"))
        .filter(product_count__gt=0)
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Product.objects.filter(is_active=True)
                .select_related("category")
                .prefetch_related(
                    Prefetch(
                        "product_images",
                        queryset=ProductImage.objects.filter(is_active=True).order_by(
                            "id"
                        )[:1],
                        to_attr="first_image",
                    )
                ),
                to_attr="products",
            )
        )
    )[:6]

    for category in categories_with_products:
        category.products = category.products[:4]

    random_categories = random.sample(
        list(categories_with_products), min(len(categories_with_products), 4)
    )

    random_products = random.sample(list(products), min(len(products), 6))

    banners = Banner.objects.filter(is_active=True)

    categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        "children"
    )

    categories_with_subcategories = []
    for category in categories:
        subcategories = fetch_sub_cat(category)
        categories_with_subcategories.append(
            {
                "id": category.id,
                "name": category.name,
                "sub_cat": subcategories,
            }
        )

    context = {
        "categories": random_categories,
        "products": random_products,
        "banners": banners,
        "categories_with_subcategories": categories_with_subcategories,
    }
    return render(request, "customer_portal/index.html", context)


def get_products_by_category(request):
    """
    Fetches products by category and returns them in a paginated HTML response.

    Filters products based on the category name and returns a snippet of HTML
    for the product list within the category.

    Args:
        request (HttpRequest): The HTTP request object containing the 'category' parameter.

    Returns:
        JsonResponse: A JSON response containing the HTML of the product list for the specified category.
    """
    category = request.GET.get("category")

    products = (
        Product.objects.filter(category__name=category, is_active=True)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "product_images",
                queryset=ProductImage.objects.filter(is_active=True)[:1],
                to_attr="first_image",
            )
        )
    )[:4]

    html = render(
        request,
        "customer_portal/category_wise_products.html",
        {"products": products},
    ).content.decode("utf-8")

    return JsonResponse({"html": html})


def product_details(request, id):
    """
    Fetches and renders details for a specific product.
    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the product to display.

    Returns:
        HttpResponse: Renders the 'product_detail.html' template with product details.
    """
    product = get_object_or_404(Product, id=id)
    in_wishlist = (
        UserWishList.objects.filter(user=request.user, product=product).exists()
        if request.user.is_authenticated
        else None
    )
    recommended_products = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(id=id)
        .select_related("category")
        .prefetch_related(
            Prefetch(
                "product_images",
                queryset=ProductImage.objects.filter(is_active=True)[:1],
                to_attr="first_image",
            )
        )
    )
    random_products = random.sample(
        list(recommended_products), min(len(recommended_products), 6)
    )
    chunked_products = [
        random_products[i : i + 3] for i in range(0, len(random_products), 3)
    ]
    context = {
        "product": product,
        "chunked_products": chunked_products,
        "in_wishlist": in_wishlist,
    }
    return render(request, "customer_portal/product_detail.html", context)


def product_list(request):
    """
    Renders a page listing all products, optionally filtered by category.
    Also includes categories and their subcategories for navigation.

    Args:
        request (HttpRequest): The HTTP request object, which can include a 'cat' parameter for filtering.

    Returns:
        HttpResponse: Renders the 'product_list.html' template with products and categories.
    """

    try:
        category_id = request.GET.get("cat")
        sort_by = request.GET.get("price")
        search_term = request.GET.get("search", "")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")

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
        ).order_by("id")

        # Sort by price if sort_by parameter is provided
        if sort_by == "high-to-low":
            products = products.order_by("-price")  # Descending order
        elif sort_by == "low-to-high":
            products = products.order_by("price")  # Ascending order

        # Filter products based on the price range
        if min_price and max_price:
            products = products.filter(price__gte=min_price, price__lte=max_price)

        if category_id:
            products = products.filter(category__name=category_id)

        categories = Category.objects.filter(parent__isnull=True).prefetch_related(
            "children"
        )

        categories_with_subcategories = []
        for category in categories:
            subcategories = fetch_sub_cat(category)
            categories_with_subcategories.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "sub_cat": subcategories,
                }
            )

        if search_term:
            products = products.filter(name__icontains=search_term)

        per_page = int(request.GET.get("per_page", 6))

        # Pagination settings
        paginator = Paginator(products, per_page)  # Show 5 categories per page
        page = request.GET.get("page", 1)

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context = {
            "products": products,
            "categories": categories_with_subcategories,
            "paginator": paginator,  # Paginator object
            "page_obj": products,
        }
        return render(request, "customer_portal/product_list.html", context)
    except Exception as e:
        return HttpResponse(str(e))
