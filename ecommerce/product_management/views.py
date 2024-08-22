# Standard library imports
import json

# Django imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

# Third-party imports


# Local imports
from .models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)
from admin_panel.decorators import check_user_group
from ecommerce.utils import paginated_response


# Create your views here.


@check_user_group(["inventory_manager"])
def list_all_products(request):
    try:
        return render(request, "product_management/products.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group(["inventory_manager"])
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
            products_list = paginated_response(request, products_list)

            return JsonResponse(products_list, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
def delete_attribute(request, attribute_id):
    try:
        attribute = ProductAttribute.objects.get(pk=attribute_id)
        attribute.delete()
        return JsonResponse({"success": True, "msg": "Attribute Deleted successfully"})
    except ProductAttribute.DoesNotExist:
        return JsonResponse({"error": "Attribute not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@check_user_group(["inventory_manager"])
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
            request,
            "product_management/product_add.html",
            {"categories": categories_list},
        )


@require_POST
@check_user_group(["inventory_manager"])
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
@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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
@check_user_group(["inventory_manager"])
def list_all_categories(request):
    try:
        categories_list = fetch_sub_cat()
        return render(
            request,
            "product_management/categories.html",
            {"categories": categories_list},
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


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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


@check_user_group(["inventory_manager"])
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
                "product_management/category_add.html",
                {"category": category_object, "categories": categories_list},
            )

    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})


@check_user_group(["inventory_manager"])
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


# ----------------------------------------Category---------------------------------------------
