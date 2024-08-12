"""
    views.py
"""

# Standard library imports
from datetime import datetime

# Django imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

# Third-party imports
import humanize

# Local imports
from ecommerce.utils import parse_datetimerange
from .models import Coupon
from .decorators import check_user_group


# -----------------------------------User----------------------------------------------------
@login_required(login_url="login", redirect_field_name="next")
def home(request):
    """
    Renders the home page for authenticated users.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered home page or an error message.
    """
    try:
        return render(request, "admin_panel/starter.html")
    except Exception as e:
        return HttpResponse(str(e))


def auth_user(request):
    """
    Authenticates a user based on provided credentials.

    Args:
        request (HttpRequest): The HTTP request object containing username and password.

    Returns:
        User or HttpResponse: Authenticated user or error message if authentication fails.
    """
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
    """
    Checks the groups a user belongs to and sets session data accordingly.

    Args:
        request (HttpRequest): The HTTP request object.
        user (User): The authenticated user.

    Returns:
        User or HttpResponse: The user object if successful or error message.
    """
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
    """
    Handles user login. If POST request, attempts to authenticate and log in user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to admin home if successful, otherwise renders login page
        with error message.
    """
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
    """
    Creates a new user with provided details and assigns groups.

    Args:
        request (HttpRequest): The HTTP request object containing user details.

    Returns:
        JsonResponse: Success message or error message with validation details.
    """
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
    """
    Renders the forgot password page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered forgot password page or an error message.
    """
    try:
        return render(request, "admin_panel/forgot_password.html")
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login")
def logout_view(request):
    """
    Logs out the user and redirects to login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to login page.
    """
    logout(request)
    return redirect("login")


def format_role(groups):
    """
    Formats the roles by replacing underscores with spaces and capitalizing each word.

    Args:
        groups (list): List of group names.

    Returns:
        dict: A dictionary with original group names as keys and formatted roles as values.
    """
    formatted_groups = {}
    for group in groups:
        if not group in ["customer"]:
            if "_" in group:
                role_with_spaces = group.replace("_", " ")
                formatted_groups[group] = role_with_spaces.title()
            else:
                formatted_groups[group] = group.capitalize()
    return formatted_groups


@check_user_group()
def all_users(request):
    """
    Retrieves and renders a list of all users with specific roles.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the users page with a list of users and available groups.
    """
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

        available_groups = format_role(Group.objects.values_list("name", flat=True))
        return render(
            request,
            "admin_panel/users.html",
            {"users": user_list, "available_groups": available_groups},
        )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def update_user(request):
    """
    Updates user information and group memberships.

    Args:
        request (HttpRequest): The HTTP request object containing updated user details.

    Returns:
        JsonResponse: Success message or error message with status.
    """
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
    """
    Deletes a user based on the provided user ID.

    Args:
        request (HttpRequest): The HTTP request object containing the user ID.

    Returns:
        JsonResponse: Success message or error message with status.
    """
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
    """
    Renders the page to list all coupons for users with appropriate permissions.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered coupon list page or an error message.
    """
    try:
        return render(request, "admin_panel/coupon.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group(["inventory_manager", "order_manager"])
def get_all_coupons(request):
    """
    Retrieves all active coupons and returns them as JSON.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: List of coupons in JSON format.
    """
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
                        "duration": f"{humanize.naturaldate(coupon.start_date)} to {humanize.naturaldate(coupon.end_date)}",
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
    """
    Creates a new coupon with the provided details.

    Args:
        request (HttpRequest): The HTTP request object containing coupon details.

    Returns:
        HttpResponse: Redirects to the list of coupons upon success or error message.
    """
    try:
        if request.method == "POST":
            code = request.POST.get("code")
            name = request.POST.get("name")
            discount = request.POST.get("discount")
            datetimerange = request.POST.get("datetimerange")
            description = request.POST.get("description")

            start_date, end_date = parse_datetimerange(datetimerange)

            Coupon.objects.create(
                code=code,
                name=name,
                discount=discount,
                start_date=start_date,
                end_date=end_date,
                description=description,
                created_by=request.user,
                updated_by=request.user,
            )
            return redirect("all_coupons")

    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def get_coupon_details(request, coupon_id):
    """
    Retrieves and returns the details of a specific coupon.

    Args:
        request (HttpRequest): The HTTP request object.
        coupon_id (int): The ID of the coupon to retrieve.

    Returns:
        JsonResponse: Coupon details in JSON format or error message if coupon is not found.
    """
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
    """
    Updates the details of an existing coupon.

    Args:
        request (HttpRequest): The HTTP request object containing updated coupon details.

    Returns:
        JsonResponse: Success message or error message with status.
    """
    try:
        if request.method == "POST":
            coupon_id = request.POST.get("coupon_id")
            coupon = Coupon.objects.get(id=coupon_id)

            coupon.name = request.POST.get("name")
            coupon.code = request.POST.get("code")
            coupon.discount = request.POST.get("discount")
            coupon.description = request.POST.get("description")
            datetimerange = request.POST.get("datetimerange")
            start_date, end_date = parse_datetimerange(datetimerange)
            coupon.start_date = start_date
            coupon.end_date = end_date
            coupon.save()

            return JsonResponse(
                {"status": "success", "msg": "Coupon updated successfully."}
            )
        return JsonResponse({"status": "error"}, status=400)
    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Coupon not found"}, status=404)
    except Exception as e:
        return HttpResponse(str(e), status=500)


@login_required(login_url="login")
def delete_coupon(request):
    """
    Deletes a specific coupon based on its ID.

    Args:
        request (HttpRequest): The HTTP request object containing the coupon ID.

    Returns:
        JsonResponse: Success message or error message with status.
    """
    try:
        if request.method == "POST":
            coupon_id = request.POST.get("coupon_id")
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon:
                coupon.delete()
                return JsonResponse(
                    {"status": "success", "msg": "Coupon deleted successfully."}
                )
            else:
                return JsonResponse({"status": "error", "msg": "Coupon not found!"})
    except Exception as e:
        return HttpResponse(str(e))
