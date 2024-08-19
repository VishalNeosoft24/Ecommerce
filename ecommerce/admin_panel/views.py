# Standard library imports
from datetime import datetime

# Django imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

# Third-party imports
import humanize

# Local imports
from .forms import EmailTemplateForm, BannerForm
from ecommerce.utils import parse_datetimerange
from .models import (
    Banner,
    Coupon,
    EmailTemplate,
)
from .decorators import check_user_group
from product_management.models import Product, ProductAttribute


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


# ----------------------------------------Email Template---------------------------------------------
def list_all_email_templates(request):
    try:
        return render(request, "admin_panel/email_templates.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def get_all_email_templates(request):
    try:
        if request.method == "GET":
            email_templates = EmailTemplate.objects.all()
            email_templatelist = []
            index = 1
            for email_template in email_templates:
                email_templatelist.append(
                    {
                        "index": index,
                        "id": email_template.id,
                        "title": email_template.title,
                        "subject": email_template.subject,
                        "title": email_template.content,
                    }
                )
                index += 1
            return JsonResponse(email_templatelist, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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

            form = EmailTemplateForm()
            return render(
                request, "admin_panel/email_templates_add.html", {"form": form}
            )
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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
            return redirect(
                "all_email_templates"
            )  # Redirect to a list of email templates
    else:
        form = EmailTemplateForm(instance=email_template)
    return render(request, "admin_panel/email_templates_add.html", {"form": form})


@check_user_group()
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
def list_all_banners(request):
    try:
        return render(request, "admin_panel/banners.html")
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def get_all_banners(request):
    try:
        if request.method == "GET":
            banners = Banner.objects.filter(is_active=True).all()
            bannerlist = []
            index = 1
            for banner in banners:
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
            return JsonResponse(bannerlist, safe=False)
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
def create_banner(request):
    try:
        if request.method == "POST":
            form = BannerForm(request.POST or None, request.FILES)

            if form.is_valid():
                banner = form.save(commit=False)
                banner.created_by = request.user
                banner.updated_by = request.user
                banner.save()
                return redirect("all_banners")
            else:
                return HttpResponse(f"Form is invalid: {form.errors}")

        else:
            form = BannerForm()
            return render(request, "admin_panel/banner_add.html", {"form": form})
    except Exception as e:
        return HttpResponse(str(e))


@check_user_group()
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
            return redirect("all_banners")  # Redirect to a list of email templates
    else:
        form = BannerForm(instance=banner)
    return render(request, "admin_panel/banner_add.html", {"form": form})


@check_user_group()
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
