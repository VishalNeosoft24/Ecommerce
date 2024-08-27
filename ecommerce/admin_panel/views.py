# Standard library imports
from datetime import datetime
import json


# Django imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from django.db.utils import IntegrityError

# Third-party imports
import humanize

from admin_panel.utils import send_admin_reply_email

# Local imports
from .forms import EmailTemplateForm, BannerForm, UserOrderForm
from ecommerce.utils import build_search_query, format_datetime, parse_datetimerange
from .models import (
    Banner,
    ContactUs,
    Coupon,
    EmailTemplate,
    User,
)
from product_management.models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)
from .decorators import check_user_permission
from order_management.models import UserOrder
from .forms import FlatPageForm
from ecommerce.utils import paginated_response
from product_management.models import Product


# -----------------------------------User----------------------------------------------------
@login_required(login_url="login", redirect_field_name="next")
def home(request):
    try:
        orders = UserOrder.objects.all().count()
        products = Product.objects.filter(is_active=True).all().count()
        users = User.objects.filter(is_active=True).all().count()

        return render(
            request,
            "admin_panel/starter.html",
            {
                "total_order": orders,
                "total_product": products,
                "total_user": users,
                "queries": 10,
            },
        )
    except Exception as e:
        return HttpResponse(str(e))


def auth_user(request):
    try:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return None

        user = check_groups(request, user)
        return user
    except Exception as e:
        return HttpResponse(str(e))


def check_groups(request, user):
    try:
        available_groups = list(user.groups.values_list("name", flat=True))
        groups = []

        if "customer" in available_groups and not user.is_superuser:
            return None

        if not user.is_superuser and "order_manager" in available_groups:
            groups.append("order_manager")

        if not user.is_superuser and "inventory_manager" in available_groups:
            groups.append("inventory_manager")

        request.session["group"] = groups
        return user
    except Exception as e:
        return HttpResponse(str(e))


def login_view(request):
    try:
        if request.method == "POST":
            user = auth_user(request)
            if user is not None:
                login(request, user)
                return redirect("admin-home")
            else:
                messages.add_message(
                    request, messages.ERROR, "Invalid username or password."
                )
                return render(request, "admin_panel/login.html")
        else:
            return render(request, "admin_panel/login.html")
    except Exception as e:
        return HttpResponse(str(e))


def create_user(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            username = request.POST.get("username")
            password = request.POST.get("password")
            re_password = request.POST.get("re_password")
            groups = request.POST.getlist("group", None)

            if not password == re_password:
                messages.add_message(
                    request, messages.ERROR, "Passwords do not match. Please try again."
                )
                return render(request, "admin_panel/register.html")
            # elif not len(password) >=8:
            # 	messages.add_message(request, messages.ERROR, 'Passwords length must be greater than 8 character. Please try again.')
            # 	return render(request, 'admin_panel/register.html')

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
            )
            user.set_password(password)
            user.save()

            if len(groups) > 0:
                for group in groups:
                    customer_group = Group.objects.get(name=group)
                    user.groups.add(customer_group)
                # else:
                #     customer_group = Group.objects.get(name="customer")
                user.groups.add(customer_group)
            return JsonResponse(
                {"status": "success", "msg": "User created successfully."}
            )
        return render(request, "admin_panel/register.html")
    except IntegrityError as e:
        # Check for the duplicate username error
        if "Duplicate entry" in str(e):
            return JsonResponse(
                {
                    "status": "error",
                    "msg": "Username already exists. Please choose another username.",
                }
            )
        else:
            return JsonResponse({"status": "error", "message": str(e)})
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


def forgot_password(request):
    try:
        return render(request, "admin_panel/forgot_password.html")
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


def format_role(groups):
    formatted_groups = {}
    for group in groups:
        if not group in ["customer"]:
            if "_" in group:
                # Replace underscores with spaces and capitalize each word
                role_with_spaces = group.replace("_", " ")
                formatted_groups[group] = role_with_spaces.title()
            else:
                # Capitalize only the first letter if no underscores
                formatted_groups[group] = group.capitalize()
    return formatted_groups


def all_users(request):
    try:
        inventory_manager = Group.objects.filter(name="inventory_manager").exists()
        order_manager = Group.objects.filter(name="order_manager").exists()

        print(inventory_manager, order_manager)
        # Check users in the 'inventory_manager' group
        inventory_manager_users = User.objects.filter(
            groups__name="inventory_manager", is_active=True
        )
        print(inventory_manager_users)

        # Check users in the 'order_manager' group
        order_manager_users = User.objects.filter(
            groups__name="order_manager", is_active=True
        )
        print(order_manager_users)

        for user in User.objects.all():
            groups = [group.name for group in user.groups.all()]
            print(f"User: {user.username}, Groups: {groups}")

        users = (
            User.objects.prefetch_related("groups")
            .filter(
                Q(groups__name="inventory_manager") | Q(groups__name="order_manager"),
                is_active=True,
            )
            .distinct()
        )
        user_list = []

        for user in users:
            time_diff = (
                datetime.now(timezone.utc) - user.last_login
                if user.last_login
                else "Not logged in yet."
            )
            user_roles = user.groups.values_list("name", flat=True)

            user_list.append(
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "email": user.email,
                    "last_login": humanize.naturaltime(time_diff),
                    "roles": format_role(user_roles),
                    "role_key": list(user_roles),
                }
            )

        available_groups = format_role(Group.objects.values_list("name", flat=True))
        return render(
            request,
            "admin_panel/users.html",
            {
                "users": user_list,
                "available_groups": available_groups,
            },
        )
    except Exception as e:
        return HttpResponse(str(e))


def update_user(request):
    try:
        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            groups = request.POST.getlist("group")
            user_id = request.POST.get("user_id")

            user = User.objects.filter(id=user_id).first()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            if len(groups) > 0:
                for group in groups:
                    group_obj = Group.objects.get(name=group)
                    user.groups.add(group_obj)

            user.save()
            msg = "User Updated successfully."
            status = "success"
            return JsonResponse({"status": status, "msg": msg})

        return JsonResponse({"status": "error"}, status=400)
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login", redirect_field_name="next")
def delete_user(request):
    try:
        if request.method == "POST":
            user_id = request.POST.get("user_id")
            user = User.objects.filter(id=user_id).first()
            if user:
                user.delete()
                msg = "User Deleted successfully."
                status = "success"
            else:
                msg = "User Not Found!"
                status = "error"
            return JsonResponse({"status": status, "msg": msg})

        return JsonResponse({"status": "error"}, status=400)
    except Exception as e:
        return HttpResponse(str(e))


# -----------------------------------/User----------------------------------------------------


# ----------------------------------------Product----------------------------------------------------
@check_user_permission(
    permission_codename="product_management.view_product", type="view"
)
def list_all_products(request):
    try:
        return render(request, "product_management/products.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="product_management.view_product", type="api"
)
def get_all_products(request):
    try:
        if request.method == "GET":

            search_query = build_search_query(
                request,
                [
                    "name",
                    "quantity",
                    "price",
                ],  # Add fields you want to search
            )

            products = Product.objects.filter(search_query, is_active=True).order_by(
                "id"
            )

            response = paginated_response(request, products)
            paginated_products = response.get("data")

            products_list = []
            index = 1 + response.get("start")
            for product in paginated_products:
                # Fetch all attributes and their values
                attributes = ProductAttribute.objects.filter(product=product)
                attributes_list = []

                product_images = ProductImage.objects.filter(product=product).all()
                product_images_list = []
                product_images_list = [
                    i.image.url for i in product_images
                ]  # Use .url to get the URL

                for attribute in attributes:
                    # Get all values for this attribute
                    attribute_values = ProductAttributeValue.objects.filter(
                        product_attribute=attribute
                    )
                    values_list = [
                        attr_value.attribute_value for attr_value in attribute_values
                    ]

                    # Create a dictionary with attribute name as key and list of values as the value
                    attributes_list.append({attribute.name: values_list})

                products_list.append(
                    {
                        "index": index,
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "category": str(product.category),
                        "short_description": product.short_description,
                        "long_description": product.long_description,
                        "quantity": product.quantity,
                        "attributes": attributes_list,
                        "image": product_images_list,
                        "blank": "",
                    }
                )
                index += 1
            response["data"] = products_list
            return JsonResponse(response, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="product_management.add_productimage", type="api"
)
def file_upload_view(request):
    try:
        if request.method == "POST":
            product_id = request.POST.get("product_id", None)
            product_instance = get_object_or_404(Product, id=product_id)
            file = request.FILES["file"]
            uploaded_file = ProductImage.objects.create(
                image=file,
                product=product_instance,
                created_by=request.user,
                updated_by=request.user,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "image_id": uploaded_file.id,
                    "file_url": uploaded_file.image.url,
                    "msg": "File Uploded successfully",
                }
            )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="product_management.add_productattribute", type="api"
)
def handle_attributes(request):
    if request.method == "POST":
        try:
            # Parse JSON data from the request
            attributes_data = json.loads(request.POST.get("attributes_data", "[]"))
            product_id = request.POST.get("product_id")

            # Validate product_id
            if not product_id:
                return JsonResponse(
                    {"status": "error", "msg": "Product ID is required"}, status=400
                )

            # Get the Product instance
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "msg": "Product does not exist"}, status=404
                )

            # Get the user from the request (adjust this based on your authentication setup)
            user = request.user if request.user.is_authenticated else None

            # Process the data
            for attribute in attributes_data:
                for attribute_name, values in attribute.items():
                    # Create or get the ProductAttribute object
                    product_attribute, created = ProductAttribute.objects.get_or_create(
                        name=attribute_name,
                        product=product,
                        created_by=user,
                        updated_by=user,
                    )

                    # Create ProductAttributeValue objects
                    for value in values:
                        ProductAttributeValue.objects.get_or_create(
                            product_attribute=product_attribute,
                            attribute_value=value,
                            created_by=user,
                            updated_by=user,
                        )

            # Return a JSON response indicating success
            return JsonResponse(
                {
                    "status": "success",
                    "msg": "Attribute added successfully",
                    "data": attributes_data,
                }
            )

        except json.JSONDecodeError as e:
            return JsonResponse(
                {"status": "error", "msg": "Invalid JSON data"}, status=400
            )

    return JsonResponse(
        {"status": "error", "msg": "Invalid request method"}, status=405
    )


@check_user_permission(
    permission_codename="product_management.change_productattribute", type="api"
)
def update_attribute(request, id):
    if request.method == "GET":
        try:
            attribute = ProductAttribute.objects.get(pk=id)
            data = {
                "name": attribute.name,
                "values": list(
                    attribute.product_attribute_key.values_list(
                        "attribute_value", flat=True
                    )
                ),
            }
            return JsonResponse(data)
        except ProductAttribute.DoesNotExist:
            return JsonResponse({"error": "Attribute not found"}, status=404)

    elif request.method == "POST":
        try:
            attribute_id = request.POST.get("attribute_id")
            attribute_name = request.POST.get("attribute_name")
            values = request.POST.getlist("values[]")

            # Fetch and update the attribute
            attribute = ProductAttribute.objects.get(pk=attribute_id)
            attribute.name = attribute_name
            attribute.save()

            # Clear existing values
            ProductAttributeValue.objects.filter(product_attribute=attribute).delete()

            # Check if values list is not empty before attempting to create new entries
            if values:
                for value in values:
                    ProductAttributeValue.objects.create(
                        product_attribute=attribute,
                        attribute_value=value,
                        created_by=request.user,  # Assuming you want to set created_by
                        updated_by=request.user,
                    )
            else:
                return JsonResponse({"error": "Values list is empty"}, status=400)

            return JsonResponse({"success": True})

        except ProductAttribute.DoesNotExist:
            return JsonResponse({"error": "Attribute not found"}, status=404)
        except Exception as e:
            # Return the error message with status 400 for debugging purposes
            return JsonResponse({"error": str(e)}, status=400)


@check_user_permission(
    permission_codename="product_management.delete_productattribute", type="api"
)
def delete_attribute(request, attribute_id):
    try:
        attribute = ProductAttribute.objects.get(pk=attribute_id)
        attribute.delete()
        return JsonResponse({"success": True, "msg": "Attribute Deleted successfully"})
    except ProductAttribute.DoesNotExist:
        return JsonResponse({"error": "Attribute not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@check_user_permission(permission_codename="product_management.add_product", type="api")
def add_product(request):
    if request.method == "POST":
        # Get product details from POST request
        product_name = request.POST.get("product_name")
        product_id = request.POST.get("product_id", None)
        price = request.POST.get("price")
        short_description = request.POST.get("short_description")
        long_description = request.POST.get("long_description")
        quantity = request.POST.get("stock_quantity")
        category_parent_id = request.POST.get("category_parent", None)

        # Validate required fields
        if not product_name:
            return JsonResponse(
                {"msg": "Product name is required.", "exists": True}, status=400
            )
        if not price:
            return JsonResponse(
                {"msg": "Price is required.", "exists": True}, status=400
            )
        if not short_description:
            return JsonResponse(
                {"msg": "Short description is required.", "exists": True}, status=400
            )
        if not quantity:
            return JsonResponse(
                {"msg": "Stock quantity is required.", "exists": True}, status=400
            )
        if not category_parent_id:
            return JsonResponse(
                {"msg": "Category is required.", "exists": True}, status=400
            )

        # Validate numeric fields
        try:
            price = float(price)
            quantity = int(quantity)
            if price < 0:
                return JsonResponse(
                    {
                        "msg": "Invalid input: The price cannot be negative. Please enter a positive value..",
                        "exists": True,
                    },
                    status=400,
                )
            if quantity < 0:
                return JsonResponse(
                    {"msg": "Quantity cannot be negative.", "exists": True}, status=400
                )
        except ValueError:
            return JsonResponse(
                {"msg": "Price and quantity must be valid numbers.", "exists": True},
                status=400,
            )

        # Check if a product with the same name already exists
        if product_id:
            if Product.objects.filter(id=product_id, name=product_name).exists():
                return JsonResponse(
                    {
                        "msg": "Product with this ID and name already exists.",
                        "exists": True,
                    },
                    status=400,
                )
        else:
            if Product.objects.filter(name=product_name).exists():
                return JsonResponse(
                    {"msg": "Product with this name already exists.", "exists": True},
                    status=400,
                )

        # Validate the category exists
        try:
            category = Category.objects.get(id=category_parent_id)
        except Category.DoesNotExist:
            return JsonResponse(
                {"msg": "Invalid Category.", "exists": True}, status=400
            )

        # Proceed with adding the product
        product = Product(
            name=product_name,
            price=price,
            category=category,
            short_description=short_description,
            long_description=long_description,
            quantity=quantity,
            created_by=request.user,
            updated_by=request.user,
        )
        product.save()

        # Associate category with product

        return JsonResponse(
            {"msg": "Product added successfully", "product_id": product.id}, status=200
        )
    else:
        categories_list = get_categories_list()
        return render(
            request,
            "product_management/product_add.html",
            {"categories": categories_list},
        )


@require_POST
@check_user_permission(
    permission_codename="product_management.delete_productimage", type="api"
)
def delete_file_view(request):
    image_id = request.POST.get("image_id")

    if not image_id:
        return JsonResponse({"success": False, "error": "Missing image ID"})

    product_image = get_object_or_404(ProductImage, id=image_id)

    if product_image.image:
        product_image.image.delete(save=False)  # Delete the image file from storage
        product_image.delete()  # Delete the database entry
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Image does not exist"})


@require_POST
@check_user_permission(
    permission_codename="product_management.delete_productimage", type="api"
)
def delete_all_files_view(request):
    product_id = request.POST.get("product_id")

    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product ID"})

    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)

    for product_image in product_images:
        if product_image.image:
            product_image.image.delete(
                save=False
            )  # Delete each image file from storage
        product_image.delete()  # Delete each database entry

    return JsonResponse({"success": True})


@check_user_permission(
    permission_codename="product_management.change_product", type="view"
)
def update_product(request, id):
    try:
        if not id:
            return JsonResponse({"status": "error", "msg": "Product ID is required."})

        product = get_object_or_404(Product, id=id)
        images = product.product_images.all()

        if request.method == "POST":
            # Get product details from POST request
            product_name = request.POST.get("product_name")
            price = request.POST.get("price")
            short_description = request.POST.get("short_description")
            long_description = request.POST.get("long_description")
            quantity = request.POST.get("stock_quantity")
            category_parent_id = request.POST.get("category_parent", None)

            # Validate required fields
            if not product_name:
                return JsonResponse(
                    {"msg": "Product name is required.", "exists": True}, status=400
                )
            if not price:
                return JsonResponse(
                    {"msg": "Price is required.", "exists": True}, status=400
                )
            if not short_description:
                return JsonResponse(
                    {"msg": "Short description is required.", "exists": True},
                    status=400,
                )
            if not long_description:
                return JsonResponse(
                    {"msg": "Long description is required.", "exists": True},
                    status=400,
                )
            if not quantity:
                return JsonResponse(
                    {"msg": "Stock quantity is required.", "exists": True}, status=400
                )
            if not category_parent_id:
                return JsonResponse(
                    {"msg": "Category is required.", "exists": True}, status=400
                )

            # Validate numeric fields
            try:
                price = float(price)
                quantity = int(quantity)
                if price < 0:
                    return JsonResponse(
                        {"msg": "Price cannot be negative.", "exists": True}, status=400
                    )
                if quantity < 0:
                    return JsonResponse(
                        {"msg": "Quantity cannot be negative.", "exists": True},
                        status=400,
                    )
            except ValueError:
                return JsonResponse(
                    {
                        "msg": "Price and quantity must be valid numbers.",
                        "exists": True,
                    },
                    status=400,
                )

            category_instance = Category.objects.get(id=category_parent_id)

            if not category_instance:
                return JsonResponse(
                    {"msg": "Invalid Category.", "exists": True}, status=400
                )

            product.name = product_name
            product.price = price
            product.short_description = short_description
            product.long_description = long_description
            product.quantity = quantity
            product.category = category_instance
            product.save()

            return JsonResponse(
                {
                    "msg": "Product Updated Successfully.",
                    "exists": False,
                    "product_id": product.id,
                },
                status=200,
            )

        else:
            attributes = ProductAttribute.objects.filter(
                product=product
            ).prefetch_related("product_attribute_key")

            return render(
                request,
                "product_management/product_add.html",
                {
                    "update_product": product,
                    "categories": get_categories_list(),
                    "images": images,
                    "attributes": attributes,
                },
            )
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_permission(
    permission_codename="product_management.delete_product", type="api"
)
def delete_product(request):
    try:
        product_id = request.POST.get("product_id", None)
        if not product_id:
            return JsonResponse({"status": "error", "msg": "Product ID is required."})

        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse(
            {"status": "success", "msg": "Product deleted successfully."}
        )
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


# -----------------------------------/Product----------------------------------------------------


# ----------------------------------------Category---------------------------------------------
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@check_user_permission(
    permission_codename="product_management.view_category", type="view"
)
def list_all_categories(request):
    try:
        # Fetch and order the top-level categories
        categories_list = Category.objects.filter(parent=None).order_by("id")
        # Get the number of items per page from the request, with a default of 5
        per_page = request.GET.get("per_page", 5)
        print("per_page: ", per_page)

        # Pagination settings
        paginator = Paginator(categories_list, per_page)  # Show 5 categories per page
        page = request.GET.get("page", 1)

        try:
            categories = paginator.page(page)
        except PageNotAnInteger:
            categories = paginator.page(1)
        except EmptyPage:
            categories = paginator.page(paginator.num_pages)

        # Get subcategories for the current page's categories
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

        start_index = categories.start_index()
        end_index = categories.end_index()
        total_entries = paginator.count

        return render(
            request,
            "product_management/categories.html",
            {
                "categories": categories,
                "categories_with_subcategories": categories_with_subcategories,
                "start_index": start_index,
                "end_index": end_index,
                "total_entries": total_entries,
            },
        )
    except Exception as e:
        return HttpResponse(str(e))


def fetch_sub_cat(category):
    subcategories = Category.objects.filter(parent=category).order_by("name")

    subcategories_list = []
    for subcategory in subcategories:
        subcategories_list.append(
            {
                "id": subcategory.id,
                "name": subcategory.name,
                "sub_cat": fetch_sub_cat(
                    subcategory
                ),  # Recursive call for further subcategories
            }
        )
    return subcategories_list


@check_user_permission(
    permission_codename="product_management.view_category", type="api"
)
def get_all_categories(request):
    try:
        if request.method == "GET":
            categories_list = fetch_sub_cat()
            return JsonResponse(categories_list, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


def get_categories_list(exclude_ids=None):
    categories = Category.objects.all()
    # exclude current ids
    if exclude_ids:
        categories = categories.exclude(id__in=exclude_ids)
    categories_list = []
    for category in categories:
        categories_list.append(
            {
                "id": category.id,
                "name": category.name,
                "parent": str(category.parent),
                "description": category.description,
                "path": str(category),
            }
        )
    return categories_list


@check_user_permission(
    permission_codename="product_management.add_category", type="view"
)
def add_category(request):
    try:
        if request.method == "POST":
            category_name = request.POST.get("category_name", None)
            parent_category_id = request.POST.get("category_parent", None)
            category_description = request.POST.get("category_description", "").strip()

            # Validations
            errors = []

            if not category_name:
                errors.append("Category name is required.")

            # Check if category with the same name already exists under the same parent
            if category_name:
                if parent_category_id:
                    existing_category = Category.objects.filter(
                        name=category_name, parent_id=parent_category_id
                    ).exists()
                    if existing_category:
                        errors.append(
                            "A category with this name already exists under the selected parent."
                        )
                else:
                    existing_category = Category.objects.filter(
                        name=category_name
                    ).exists()
                    if existing_category:
                        errors.append(
                            "A category with this name already exists under the selected parent."
                        )

            # If there are any validation errors, display them and re-render the form
            if errors:
                for error in errors:
                    messages.error(request, error)
                categories_list = get_categories_list()
                return render(
                    request,
                    "product_management/category_add.html",
                    {
                        "categories": categories_list,
                        "category_name": category_name,
                        "category_description": category_description,
                        "parent_category_id": parent_category_id,
                    },
                )

            # If no parent category is selected, set it to None
            if parent_category_id:
                parent_category_instance = get_object_or_404(
                    Category, id=parent_category_id
                )
            else:
                parent_category_instance = None

            # Save the new category
            category = Category(
                name=category_name,
                parent=parent_category_instance,
                description=category_description,
                created_by=request.user,
                updated_by=request.user,
            )
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect("all_categories")

        else:
            categories_list = get_categories_list()
            return render(
                request,
                "product_management/category_add.html",
                {"categories": categories_list},
            )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="product_management.change_category", type="view"
)
def update_category(request, id):
    try:
        if not id:
            return JsonResponse({"status": "error", "msg": "Category ID is required."})

        category_object = Category.objects.get(id=id)
        excluded_categories_id = [category_object.id]
        categories_list = get_categories_list(exclude_ids=excluded_categories_id)

        if request.method == "POST":

            category_object.name = request.POST.get("category_name", None)
            parent_category_id = request.POST.get("category_parent", None)

            if parent_category_id:

                parent_category_instance = get_object_or_404(
                    Category, id=parent_category_id
                )

                if category_object.name in str(parent_category_instance):
                    parent_category_instance.parent = category_object.parent
                    parent_category_instance.save()

                category_object.parent = parent_category_instance

            else:

                category_object.parent = None

            category_object.description = request.POST.get("category_description")
            category_object.save()
            messages.success(request, "Category Updated successfully!")

            return redirect("all_categories")
        else:
            return render(
                request,
                "product_management/category_add.html",
                {"category": category_object, "categories": categories_list},
            )

    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_permission(
    permission_codename="product_management.delete_category", type="api"
)
def delete_category(request):
    try:
        category_id = request.POST.get("category_id", None)
        if not category_id:
            return JsonResponse({"status": "error", "msg": "Category ID is required."})

        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, "Category Deleted successfully!")
        return JsonResponse(
            {"status": "success", "msg": "Category deleted successfully."}
        )
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


# ----------------------------------------Category---------------------------------------------


# ----------------------------------------Coupon---------------------------------------------
@check_user_permission(permission_codename="admin_panel.view_coupon", type="view")
def list_all_coupons(request):
    try:
        return render(request, "admin_panel/coupon.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.view_coupon", type="view")
def get_all_coupons(request):
    try:
        if request.method == "GET":
            coupons = Coupon.objects.filter(is_active=True).order_by("id")
            response = paginated_response(request, coupons)
            paginated_coupons = response.get("data")
            coupons_list = []
            index = 1 + response.get("start")
            for coupon in paginated_coupons:
                coupons_list.append(
                    {
                        "index": index,
                        "id": coupon.id,
                        "name": coupon.name,
                        "code": coupon.code,
                        "desc": coupon.description,
                        "count": coupon.count,
                        "duration": str(humanize.naturaldate(coupon.start_date))
                        + " to "
                        + str(humanize.naturaldate(coupon.end_date)),
                        "blank": "",
                    }
                )
                index += 1
            response["data"] = coupons_list
            return JsonResponse(response, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.add_coupon", type="view")
def create_coupon(request):
    try:
        if request.method == "POST":
            code = request.POST.get("code")
            name = request.POST.get("name")
            discount = request.POST.get("discount")
            datetimerange = request.POST.get("datetimerange")
            description = request.POST.get("description")

            # Basic validations
            if not code:
                return JsonResponse({"error": "Coupon code is required."}, status=400)
            if not name:
                return JsonResponse({"error": "Coupon name is required."}, status=400)
            if not discount:
                return JsonResponse(
                    {"error": "Discount value is required."}, status=400
                )
            try:
                discount = float(discount)
                if discount <= 0:
                    return JsonResponse(
                        {"error": "Discount must be a positive number."}, status=400
                    )
            except ValueError:
                return JsonResponse({"error": "Invalid discount value."}, status=400)

            if not datetimerange:
                return JsonResponse(
                    {"error": "Date and time range is required."}, status=400
                )
            try:
                start_date, end_date = parse_datetimerange(datetimerange)
                if start_date >= end_date:
                    return JsonResponse(
                        {"error": "End date must be after the start date."}, status=400
                    )
            except Exception as e:
                return JsonResponse({"error": f"Invalid date range: {e}"}, status=400)

            if not description:
                return JsonResponse({"error": "Description is required."}, status=400)

            # Create and save the coupon
            coupon = Coupon(
                code=code,
                name=name,
                discount=discount,
                start_date=start_date,
                end_date=end_date,
                description=description,
                created_by=request.user,
                updated_by=request.user,
            )
            coupon.save()
            return JsonResponse({"success": "Coupon created successfully."})

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


@check_user_permission(permission_codename="admin_panel.view_coupon", type="api")
def get_coupon_details(request, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
        coupon_details = {
            "id": coupon.id,
            "name": coupon.name,
            "code": coupon.code,
            "discount": coupon.discount,
            "is_active": coupon.is_active,
            "description": coupon.description,
            "start_date": coupon.start_date,
            "end_date": coupon.end_date,
        }
        return JsonResponse({"status": "success", "data": coupon_details})
    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Coupon not found"}, status=404)
    except Exception as e:
        return HttpResponse(str(e), status=500)


@check_user_permission(permission_codename="admin_panel.change_coupon", type="api")
def update_coupon(request):
    try:
        coupon_id = request.POST.get("coupon_id")
        coupon = Coupon.objects.get(id=coupon_id)

        # Update coupon fields with form data
        coupon.name = request.POST.get("name")
        coupon.code = request.POST.get("code")
        coupon.is_active = True
        coupon.discount = request.POST.get("discount")
        coupon.description = request.POST.get("description")
        datetimerange = request.POST.get("datetimerange_edit")

        start_date, end_date = parse_datetimerange(datetimerange)

        coupon.start_date = start_date
        coupon.end_date = end_date

        coupon.save()

        return JsonResponse(
            {"status": "success", "msg": "Coupon updated successfully."}
        )
    except Coupon.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Coupon not found."})
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_permission(permission_codename="admin_panel.delete_coupon", type="api")
def delete_coupon(request):
    coupon_id = request.POST.get("coupon_id", None)
    if not coupon_id:
        return JsonResponse({"status": "error", "msg": "Coupon ID is required."})

    try:
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.delete()
        return JsonResponse(
            {"status": "success", "msg": "Coupon deleted successfully."}
        )
    except Coupon.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Coupon not found."})


# ----------------------------------------Email Template---------------------------------------------
@check_user_permission(
    permission_codename="admin_panel.view_emailtemplate", type="view"
)
def list_all_email_templates(request):
    try:
        return render(request, "admin_panel/email_templates.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.view_emailtemplate", type="api")
def get_all_email_templates(request):
    try:
        if request.method == "GET":
            email_templates = EmailTemplate.objects.order_by("id")
            response = paginated_response(request, email_templates)
            paginated_email_templates = response.get("data")

            email_templatelist = []
            index = 1 + response.get("start")
            for email_template in paginated_email_templates:
                email_templatelist.append(
                    {
                        "index": index,
                        "id": email_template.id,
                        "title": email_template.title,
                        "subject": email_template.subject,
                        "content": email_template.content,
                    }
                )
                index += 1
            response["data"] = email_templatelist
            return JsonResponse(response, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.add_emailtemplate", type="view")
def create_email_template(request):
    try:
        if request.method == "POST":
            form = EmailTemplateForm(request.POST or None)
            if form.is_valid():
                email_template = form.save(commit=False)
                email_template.created_by = request.user
                email_template.updated_by = request.user
                email_template.save()
                return redirect("all_email_templates")
            else:
                return render(
                    request, "admin_panel/email_templates_add.html", {"form": form}
                )

        else:
            form = EmailTemplateForm()
            return render(
                request, "admin_panel/email_templates_add.html", {"form": form}
            )

    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="admin_panel.change_emailtemplate", type="view"
)
def update_email_template(request, id):
    try:
        email_template = EmailTemplate.objects.get(id=id)
    except EmailTemplate.DoesNotExist:
        return JsonResponse(
            {"status": "error", "msg": "Email Template not found"}, status=404
        )

    if request.method == "POST":
        form = EmailTemplateForm(request.POST, instance=email_template)
        if form.is_valid():
            email_template = form.save(commit=False)
            email_template.updated_by = request.user
            email_template.save()
            return redirect("all_email_templates")
        else:
            return render(
                request, "admin_panel/email_templates_add.html", {"form": form}
            )
    else:
        form = EmailTemplateForm(instance=email_template)
    return render(request, "admin_panel/email_templates_add.html", {"form": form})


@check_user_permission(
    permission_codename="admin_panel.delete_emailtemplate", type="api"
)
def delete_email_template(request):
    if request.method == "POST":
        try:
            email_template_id = request.POST.get("email_template_id")
            if not email_template_id:
                return JsonResponse(
                    {"status": "error", "msg": "Email Template ID is required."}
                )

            email_template = EmailTemplate.objects.get(id=email_template_id)
            email_template.delete()
            return JsonResponse(
                {"status": "success", "msg": "Email Template deleted successfully."}
            )

        except EmailTemplate.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "Email Template not found."})
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})
    return JsonResponse({"status": "error", "msg": "Invalid request method."})


# ----------------------------------------Banner---------------------------------------------
@check_user_permission(permission_codename="admin_panel.view_banner", type="view")
def list_all_banners(request):
    try:
        return render(request, "admin_panel/banners.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.view_banner", type="api")
def get_all_banners(request):
    try:
        if request.method == "GET":
            banners = Banner.objects.filter(is_active=True).order_by("id")
            response = paginated_response(request, banners)
            paginated_banners = response.get("data")
            bannerlist = []
            index = 1 + response.get("start")
            for banner in paginated_banners:
                bannerlist.append(
                    {
                        "id": banner.id,
                        "index": index,
                        "title": banner.title,
                        "image": banner.image.url if banner.image else "",
                        "url": banner.url,
                    }
                )
                index += 1
            response["data"] = bannerlist
            return JsonResponse(response, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.add_banner", type="view")
def create_banner(request):
    try:
        if request.method == "POST":
            form = BannerForm(request.POST or None, request.FILES)

            if form.is_valid():
                banner = form.save(commit=False)
                banner.created_by = request.user
                banner.updated_by = request.user
                banner.is_active = True
                banner.save()
                return redirect("all_banners")
            else:
                return render(request, "admin_panel/banner_add.html", {"form": form})

        else:
            form = BannerForm()
            return render(request, "admin_panel/banner_add.html", {"form": form})
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.change_banner", type="view")
def update_banner(request, id):
    try:
        banner = Banner.objects.get(id=id)
    except Banner.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Banner not found"}, status=404)

    if request.method == "POST":
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            banner = form.save(commit=False)
            banner.updated_by = request.user
            banner.save()
            return redirect("all_banners")
        else:
            return render(request, "admin_panel/banner_add.html", {"form": form})
    else:
        form = BannerForm(instance=banner)
    return render(request, "admin_panel/banner_add.html", {"form": form})


@check_user_permission(permission_codename="admin_panel.delete_banner", type="api")
def delete_banner(request):
    if request.method == "POST":
        try:
            banner_id = request.POST.get("banner_id")
            if not banner_id:
                return JsonResponse(
                    {"status": "error", "msg": "Banner ID is required."}
                )

            banner = Banner.objects.get(id=banner_id)
            banner.delete()
            return JsonResponse(
                {"status": "success", "msg": "Banner deleted successfully."}
            )

        except Banner.DoesNotExist:
            return JsonResponse(
                {"status": "error", "msg": "Banner Template not found."}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)})
    return JsonResponse({"status": "error", "msg": "Invalid request method."})


# ----------------------------------------FlatPages---------------------------------------------
@check_user_permission(permission_codename="flatpages.add_flatpage", type="view")
def create_flatpage(request):
    if request.method == "POST":
        form = FlatPageForm(request.POST)
        if form.is_valid():
            flatpage = form.save(commit=False)
            flatpage.save()
            # Ensure the current site is always included
            current_site = Site.objects.get_current()

            # Check if 'sites' exists in cleaned_data
            sites = form.cleaned_data.get("sites", [])
            if current_site not in sites:
                flatpage.sites.add(current_site)

            form.save_m2m()  # Save the many-to-many relationship (sites)
            return redirect("all_flatpages")  # Redirect to a list or detail view
        else:
            render(request, "admin_panel/flatpage_add.html", {"form": form})
    else:
        form = FlatPageForm(initial={"sites": [Site.objects.get_current()]})
    return render(request, "admin_panel/flatpage_add.html", {"form": form})


@check_user_permission(permission_codename="flatpages.view_flatpage", type="view")
def flatpage_list(request):
    try:
        return render(request, "admin_panel/flatpage_list.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="flatpages.view_flatpage", type="api")
def get_all_flatpage(request):
    try:
        flatpages = FlatPage.objects.all().order_by("id")
        response = paginated_response(request, flatpages)
        paginated_flatpages = response.get("data")
        flatpages_list = []
        index = 1
        for flatpage in paginated_flatpages:
            flatpages_list.append(
                {
                    "id": flatpage.id,
                    "index": index,
                    "title": flatpage.title,
                    "url": flatpage.url,
                    "abs_url": flatpage.get_absolute_url(),
                }
            )
            index += 1
        response["data"] = flatpages_list
        return JsonResponse(response, safe=False)

    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="flatpages.change_flatpage", type="view")
def update_flatpage(request, flatpage_id):
    flatpage = get_object_or_404(FlatPage, pk=flatpage_id)
    if request.method == "POST":
        form = FlatPageForm(request.POST, instance=flatpage)
        if form.is_valid():
            form.save()
            return redirect("all_flatpages")
    else:
        form = FlatPageForm(instance=flatpage)
    return render(request, "admin_panel/flatpage_add.html", {"form": form})


@check_user_permission(permission_codename="flatpages.delete_flatpage", type="api")
def delete_flatpage(request, flatpage_id):
    flatpage = get_object_or_404(FlatPage, pk=flatpage_id)
    if request.method == "POST":
        flatpage.delete()
        return JsonResponse(
            {"status": "success", "msg": "FlatPage Deleted Successfully"}
        )


# ----------------------------------------/FlatPages---------------------------------------------


# ----------------------------------------Orders---------------------------------------------


@check_user_permission(
    permission_codename="order_management.view_userorder", type="view"
)
def list_all_orders(request):
    try:
        print("-----------------------------")
        return render(request, "admin_panel/orders.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="order_management.view_userorder", type="api"
)
def get_all_orders(request):
    try:
        search_query = build_search_query(
            request,
            [
                "user__username",
                "awb_no",
            ],  # Add fields you want to search
        )

        orders = (
            UserOrder.objects.filter(search_query)
            .prefetch_related("order_details")
            .order_by("id")
        )
        response = paginated_response(request, orders)
        paginated_orders = response.get("data")

        orders_list = []
        index = 1 + response.get("start")
        for order in paginated_orders:
            order_details = [
                {
                    "product": detail.product.name,
                    "quantity": detail.quantity,
                    "amount": detail.amount,
                }
                for detail in order.order_details.all()
            ]
            orders_list.append(
                {
                    "id": order.id,
                    "index": index,
                    "user": str(order.user),
                    "shipping_method": order.get_shipping_method_display(),
                    "awb_no": order.awb_no,
                    "payment_gateway": str(order.payment_gateway),
                    "transaction_id": order.transaction_id,
                    "created_at": format_datetime(order.created_at),
                    "status": order.get_status_display(),
                    "grand_total": order.grand_total,
                    "shipping_charges": order.shipping_charges,
                    "coupon": str(order.coupon),
                    "order_details": order_details,
                }
            )
            index += 1
        response["data"] = orders_list
        return JsonResponse(response, safe=False)

    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(
    permission_codename="order_management.change_userorder", type="view"
)
def update_order(request, order_id):
    order = UserOrder.objects.prefetch_related(
        "order_details",
    ).get(pk=order_id)

    for ord in order.order_details.all():
        print(ord)
    # order = get_object_or_404(UserOrder, pk=order_id)
    if request.method == "POST":
        form = UserOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("all_orders")
    else:
        form = UserOrderForm(instance=order)
    return render(
        request, "admin_panel/order_update.html", {"form": form, "order": order}
    )


# ----------------------------------------/Orders---------------------------------------------


# ----------------------------------------/Contact Us---------------------------------------------
def list_all_contact_us(request):
    try:
        return render(request, "admin_panel/contact_us.html")
    except Exception as e:
        return HttpResponse(str(e))


@login_required
def get_all_contact_us_queries(request):
    # Server-side processing for DataTables
    contact_us_queries = ContactUs.objects.all().order_by("created_at")
    response = paginated_response(request, contact_us_queries)
    paginated_contact_us_queries = response.get("data")

    index = 1 + response.get("start")
    contact_us_queries_list = []
    for query in paginated_contact_us_queries:
        contact_us_queries_list.append(
            {
                "id": query.id,
                "index": index,
                "first_name": query.first_name,
                "last_name": query.last_name,
                "email": query.email,
                "phone_number": query.phone_number,
                "message": query.message,
                "admin_reply": query.note_admin,
            }
        )
        index += 1
    response["data"] = contact_us_queries_list
    return JsonResponse(response, safe=False)


def contact_us_query_detail(request, id):
    try:
        contact_us_query = ContactUs.objects.get(id=id)
        if request.method == "GET":
            return render(
                request,
                "admin_panel/contact_us_detail.html",
                {"query": contact_us_query},
            )
        else:
            template = EmailTemplate.objects.filter(title="Contact Us Reply").first()
            reply = request.POST.get("admin_reply", None)
            contact_us_query.note_admin = reply
            contact_us_query.save()

            send_admin_reply_email(
                contact_us_query,
                contact_us_query.message,
                contact_us_query.note_admin,
                template,
            )
            messages.success(request, "Send Reply Successfully!")
            return JsonResponse({"status": "success", "msg": "Send Reply Successfully"})
    except Exception as e:
        return HttpResponse(str(e))


@check_user_permission(permission_codename="admin_panel.delete_contactus", type="view")
def delete_contact_us_query(request):
    query_id = request.POST.get("query_id")
    if query_id:
        contact_us = get_object_or_404(ContactUs, pk=query_id)
        contact_us.delete()
        return JsonResponse({"status": "success", "msg": "Query deleted successfully"})
    else:
        return JsonResponse({"status": "error", "msg": "Invalid request"})


# ----------------------------------------/Contact Us---------------------------------------------
