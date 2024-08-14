# Standard library imports
from datetime import datetime
import json

# Django imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

# Third-party imports
import humanize

# Local imports
from ecommerce.utils import parse_datetimerange
from .models import (
    Category,
    Coupon,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)
from .decorators import check_user_group


# -----------------------------------User----------------------------------------------------
@login_required(login_url="login", redirect_field_name="next")
def home(request):
    try:
        return render(request, "admin_panel/starter.html")
    except Exception as e:
        return HttpResponse(str(e))


def auth_user(request):
    try:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.add_message(
                request, messages.ERROR, "Invalid username or password."
            )
            return render(request, "admin_panel/login.html")

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

        if user.is_superuser:
            groups.append("Admin")

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
            if user:
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


@check_user_group([])
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
            else:
                customer_group = Group.objects.get(name="customer")
                user.groups.add(customer_group)
            return JsonResponse({"status": "success"})
        return render(request, "admin_panel/register.html")
    except Exception as e:
        return HttpResponse(str(e))


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


@check_user_group()
def all_users(request):
    try:
        users = (
            User.objects.prefetch_related("groups")
            .filter(
                Q(groups__name="inventory_manager")
                | Q(groups__name="Admin")
                | Q(groups__name="order_manager")
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

        product = get_object_or_404(Product, id=198)
        print("product: ", product)
        attributes = ProductAttribute.objects.filter(product=product).prefetch_related(
            "product_attribute_key"
        )

        available_groups = format_role(Group.objects.values_list("name", flat=True))
        return render(
            request,
            "admin_panel/users.html",
            {
                "users": user_list,
                "available_groups": available_groups,
                "attributes": attributes,
            },
        )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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


@check_user_group(["inventory_manager", "order_manager"])
def list_all_coupons(request):
    try:
        return render(request, "admin_panel/coupon.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group(["inventory_manager", "order_manager"])
def get_all_coupons(request):
    try:
        if request.method == "GET":
            coupons = Coupon.objects.filter(is_active=True).all()
            coupons_list = []
            index = 1
            for coupon in coupons:
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
            return JsonResponse(coupons_list, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


# ----------------------------------------Coupon---------------------------------------------
@check_user_group()
def create_coupon(request):
    try:
        if request.method == "POST":
            code = request.POST.get("code")
            name = request.POST.get("name")
            discount = request.POST.get("discount")
            datetimerange = request.POST.get("datetimerange")
            description = request.POST.get("description")

            start_date, end_date = parse_datetimerange(datetimerange)

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
            return redirect("all_coupons")

    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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


@login_required(login_url="login")
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


@check_user_group()
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


# ----------------------------------------Product---------------------------------------------
def list_all_products(request):
    try:
        return render(request, "admin_panel/products.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def get_all_products(request):
    try:
        if request.method == "GET":
            products = Product.objects.filter(is_active=True).all()
            products_list = []
            index = 1
            for product in products:
                # Fetch all attributes and their values
                attributes = ProductAttribute.objects.filter(product=product)
                attributes_list = []

                product_images = ProductImage.objects.filter(product=product).all()
                product_images_list = []
                product_images_list = [
                    i.image.url for i in product_images
                ]  # Use .url to get the URL
                print("product_images_list: ", product_images_list)

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
            print("products_list = ", products_list)
            return JsonResponse(products_list, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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
            values = request.POST.getlist("values")

            # Fetch and update the attribute
            attribute = ProductAttribute.objects.get(pk=attribute_id)
            attribute.name = attribute_name
            attribute.save()

            # Clear existing values
            ProductAttributeValue.objects.filter(product_attribute=attribute).delete()

            # Add new values
            for value in values:
                ProductAttributeValue.objects.create(
                    product_attribute=attribute,
                    attribute_value=value,
                    created_by=request.user,  # Assuming you want to set created_by
                )

            return JsonResponse({"success": True})

        except ProductAttribute.DoesNotExist:
            return JsonResponse({"error": "Attribute not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# def add_product(request):
#     if request.method == "POST":
#         product_name = request.POST.get("product_name")
#         product_id = request.POST.get(
#             "product_id", None
#         )  # Default to None for new products
#         # Check if a product with the same name already exists (excluding the product with the current ID if provided)
#         if product_id:
#             if Product.objects.filter(id=product_id, name=product_name).exists():
#                 return JsonResponse(
#                     {
#                         "msg": "Product with this ID and name already exists.",
#                         "exists": True,
#                     }
#                 )
#             else:
#                 return JsonResponse({"msg": "Do not mess with ID.", "exists": True})
#         else:
#             if Product.objects.filter(name=product_name).exists():
#                 return JsonResponse(
#                     {"msg": "Product with this name already exists.", "exists": True}
#                 )

#         # Proceed with adding the product
#         product = Product(
#             name=product_name,
#             price=request.POST.get("price"),
#             short_description=request.POST.get("short_description"),
#             quantity=request.POST.get("stock_quantity"),
#             long_description=request.POST.get("long_description"),
#             created_by=request.user,
#             updated_by=request.user,
#         )
#         product.save()

#         return JsonResponse(
#             {"msg": "Product added successfully", "product_id": product.id}, status=200
#         )
#     else:
#         categories_list = get_categories_list()
#         return render(
#             request, "admin_panel/product_add.html", {"categories": categories_list}
#         )


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
                    {"msg": "Price cannot be negative.", "exists": True}, status=400
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
            request, "admin_panel/product_add.html", {"categories": categories_list}
        )


@require_POST
def delete_file_view(request):
    image_id = request.POST.get("image_id")
    print("image_id: ", image_id)

    if not image_id:
        return JsonResponse({"success": False, "error": "Missing image ID"})

    product_image = get_object_or_404(ProductImage, id=image_id)
    print("product_image: ", product_image)

    if product_image.image:
        product_image.image.delete(save=False)  # Delete the image file from storage
        product_image.delete()  # Delete the database entry
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Image does not exist"})


@require_POST
def delete_all_files_view(request):
    product_id = request.POST.get("product_id")
    print("product_id: ", product_id)

    if not product_id:
        return JsonResponse({"success": False, "error": "Missing product ID"})

    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    print("product_images: ", product_images)

    for product_image in product_images:
        print("=================")
        if product_image.image:
            product_image.image.delete(
                save=False
            )  # Delete each image file from storage
        product_image.delete()  # Delete each database entry

    return JsonResponse({"success": True})


@check_user_group()
def update_product(request, id):
    try:
        if not id:
            return JsonResponse({"status": "error", "msg": "Product ID is required."})

        product = get_object_or_404(Product, id=id)
        images = product.product_images.all()

        if request.method == "POST":
            print("===============")
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
            print("product", product)

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

            for attribute in attributes:
                print(f"Attribute: {attribute.name}")
                for value in attribute.product_attribute_key.all():
                    print(f" - Value: {value.attribute_value}")

            print("========", attributes)

            return render(
                request,
                "admin_panel/product_add.html",
                {
                    "update_product": product,
                    "categories": get_categories_list(),
                    "images": images,
                    "attributes": attributes,
                },
            )
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_group()
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


# ----------------------------------------Category---------------------------------------------
@check_user_group()
def list_all_categories(request):
    try:
        categories_list = fetch_sub_cat()
        return render(
            request, "admin_panel/categories.html", {"categories": categories_list}
        )
    except Exception as e:
        return HttpResponse(str(e))


def fetch_sub_cat(parent=None):
    categories = Category.objects.filter(parent=parent)
    categories_list = []
    color_classes = ["card-primary", "card-warning", "card-success", "card-info"]
    index = 1

    for category in categories:
        categories_list.append(
            {
                "index": index,
                "id": category.id,
                "name": category.name,
                "sub_cat": fetch_sub_cat(category),
            }
        )
        index += 1
    return categories_list


@check_user_group()
def get_all_categories(request):
    try:
        if request.method == "GET":
            categories_list = fetch_sub_cat()
            return JsonResponse(categories_list, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


def get_categories_list():
    categories = Category.objects.all()
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


@check_user_group()
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
                    "admin_panel/category_add.html",
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
                "admin_panel/category_add.html",
                {"categories": categories_list},
            )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def update_category(request, id):
    try:
        if not id:
            return JsonResponse({"status": "error", "msg": "Category ID is required."})

        category_object = Category.objects.get(id=id)
        categories_list = get_categories_list()

        if request.method == "POST":
            category_object.name = request.POST.get("category_name", None)
            parent_category_id = request.POST.get("category_parent", None)
            if parent_category_id:
                parent_category_instance = get_object_or_404(
                    Category, id=parent_category_id
                )
                category_object.parent = parent_category_instance
            else:
                category_object.parent = None
            category_object.description = request.POST.get("category_description")
            category_object.save()
            return redirect("all_categories")
        else:
            return render(
                request,
                "admin_panel/category_add.html",
                {"category": category_object, "categories": categories_list},
            )

    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_group()
def delete_category(request):
    try:
        category_id = request.POST.get("category_id", None)
        if not category_id:
            return JsonResponse({"status": "error", "msg": "Category ID is required."})

        category = Category.objects.get(id=category_id)
        category.delete()
        return JsonResponse(
            {"status": "success", "msg": "Category deleted successfully."}
        )
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})
