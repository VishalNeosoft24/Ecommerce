# Django core imports
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.core.paginator import Paginator


# Local app imports
from admin_panel.models import Address, NewsLetter
from admin_panel.utils import send_user_credentials_email
from order_management.models import UserOrder
from user_management.forms import AddressForm, UpdateUserForm
from .models import User
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ContactUsForm, NewsLetterForm


def register_page(request):
    """
    Handles user registration.

    Validates user input for username, email, and password, and checks for
    existing users with the same username or email. If validation passes,
    creates a new user, logs them in, and redirects to the home page. If
    validation fails, displays appropriate error messages.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'login.html' template with error messages
        or redirects to the home page upon successful registration.
    """

    try:
        if request.method == "POST":
            # Retrieve form data
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            re_password = request.POST.get("re_password", "").strip()

            # Validate form data
            if not first_name or not last_name or not username or not password:
                messages.error(request, "All fields are required.")
                return render(request, "customer_portal/login.html")

            elif not len(password) >= 8:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Passwords length must be greater than 8 character. Please try again.",
                )
                return render(request, "customer_portal/login.html")

            if password != re_password:
                messages.error(request, "Passwords do not match. Please try again.")
                return render(request, "customer_portal/login.html")

            try:
                # Validate email format
                validate_email(email)

            except ValidationError as ve:
                # Show each validation error as a separate Toastr notification
                for error in ve.messages:
                    messages.error(request, error)
                return render(request, "customer_portal/login.html")

            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(
                    request, "Username already exists. Please choose another username."
                )
                return render(request, "customer_portal/login.html")

            if User.objects.filter(email=email).exists():
                messages.error(
                    request, "Email already in use. Please use a different email."
                )
                return render(request, "customer_portal/login.html")

            # Create the user
            try:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                )
                user.set_password(password)
                user.save()

                send_user_credentials_email(user, password)

                # Log the user in and redirect to a success page
                login(request, user)
                return redirect("home_page")
            except IntegrityError:
                messages.error(
                    request, "Username already exists. Please choose another username."
                )
                return render(request, "customer_portal/login.html")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, "customer_portal/login.html")

        # Render the registration page for GET requests
        return render(request, "customer_portal/login.html")

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, "customer_portal/login.html")


def login_page(request):
    """
    Handles user login.

    Validates user input for username and password. Authenticates the user
    and logs them in if credentials are correct. If authentication fails,
    displays an error message. For GET requests, renders the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'login.html' template with error messages
        or redirects to the home page upon successful login.
    """

    try:
        if request.method == "POST":
            # Retrieve form data
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()

            # Validate form data
            if not username or not password:
                messages.error(request, "Both username and password are required.")
                return render(request, "customer_portal/login.html")

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(request, user)
                # Redirect to a success page, e.g., home page
                return redirect("home_page")
            else:
                # Invalid credentials
                messages.error(request, "Invalid username or password.")
                return render(request, "customer_portal/login.html")

        # Render the login page for GET requests
        return render(request, "customer_portal/login.html")

    except Exception as e:
        # Handle any unexpected errors
        messages.error(request, "An error occurred: " + str(e))
        return render(request, "customer_portal/login.html")


@login_required(login_url="login_page")
def logout_page(request):
    """
    Logs out the user and redirects to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the login page after logging out the user.
    """
    cart = request.session.get("cart", {})
    logout(request)
    # Restore cart data
    request.session["cart"] = cart
    return redirect("login_page")


@login_required(login_url="login_page")
def profile_page(request):
    """
    Displays and updates the user's profile information.

    Handles GET requests to display the user's profile with a form for
    updating user details. Handles POST requests to process the form and
    update the user's profile. Redirects to the profile page after a successful
    update.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'user_profile.html' template with user
        information and the form, or redirects to the profile page after
        a successful update.
    """

    try:
        user = get_object_or_404(User, id=request.user.id)
        address = Address.objects.filter(user_id=request.user.id, active=True).all()
        orders = UserOrder.objects.filter(user=user).order_by("-created_at")[:5]

        if request.method == "POST":
            form = UpdateUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect("profile_page")  # Redirect to a profile page or similar
            else:
                render(
                    request,
                    "customer_portal/user_profile.html",
                    {
                        "form": form,
                        "user": user,
                        "address": address,
                        "orders": orders,
                    },
                )
        else:
            form = UpdateUserForm(instance=user)
        return render(
            request,
            "customer_portal/user_profile.html",
            {"form": form, "user": user, "address": address, "orders": orders},
        )
    except Exception as e:
        return HttpResponse(str(e))


@login_required(login_url="login_page")
def update_user(request, user_id):
    """
    Updates a user's profile information.

    Fetches the user by ID and handles form submission to update user details.
    Redirects to the profile page after a successful update.

    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user to update.

    Returns:
        HttpResponse: Renders the 'user_profile.html' template with the form
        for updating user details, or redirects to the profile page after
        a successful update.
    """

    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("profile_page")  # Redirect to a profile page or similar
        return render(
            request, "customer_portal/user_profile.html", {"form": form, "user": user}
        )
    else:
        form = UpdateUserForm(instance=user)
    return render(
        request, "customer_portal/user_profile.html", {"form": form, "user": user}
    )


@login_required(login_url="login_page")
def add_address(request):
    """
    Adds a new address for the logged-in user.

    Handles POST requests to save a new address associated with the logged-in user.
    Redirects to the profile page upon successful address creation.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'add_address.html' template with the form
        for adding an address, or redirects to the profile page after a
        successful address creation.
    """

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.created_by = request.user
            address.updated_by = request.user
            address.is_active = True
            address.save()
            return redirect(
                "profile_page"
            )  # Replace 'address_list' with your success URL
        else:
            return render(request, "customer_portal/add_address.html", {"form": form})

    else:
        form = AddressForm()

    return render(request, "customer_portal/add_address.html", {"form": form})


@login_required(login_url="login_page")
def update_address(request, id):
    """
    Updates an existing address for the logged-in user.

    Fetches the address by ID and handles form submission to update the address.
    Redirects to the profile page after a successful update.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the address to update.

    Returns:
        HttpResponse: Renders the 'add_address.html' template with the form
        for updating the address, or redirects to the profile page after a
        successful update.
    """

    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Address not found"}, status=404)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            address.updated_by = request.user
            address.save()
            return redirect("profile_page")
        else:
            return render(request, "customer_portal/user_profile.html", {"form": form})
    else:
        form = AddressForm(instance=address)
    return render(request, "customer_portal/add_address.html", {"form": form})


@login_required(login_url="login_page")
def delete_address(request, id):
    """
    Deletes an address for the logged-in user.

    Fetches the address by ID and deletes it. Redirects to the profile page
    after successful deletion.

    Args:
        request (HttpRequest): The HTTP request object.
        id (int): The ID of the address to delete.

    Returns:
        HttpResponse: Redirects to the profile page after successful address
        deletion, or returns a JSON response with an error message if the address
        is not found.
    """

    try:
        address = Address.objects.get(id=id)
        address.delete()
        return redirect("profile_page")
    except Address.DoesNotExist:
        return JsonResponse({"status": "error", "msg": "Address not found"}, status=404)


class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Custom view for handling password reset requests.

    Uses a custom template for password reset and defines the URL to redirect
    to after a successful password reset request.

    Attributes:
        template_name (str): The path to the custom password reset form template.
        success_url (str): The URL to redirect to after a successful password
        reset request.
    """

    template_name = "registration/custom_password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordChangeView(PasswordChangeView):
    """
    Custom view for handling password change requests.

    Uses a custom template and form class for changing the password, and
    defines the URL to redirect to after a successful password change.

    Attributes:
        template_name (str): The path to the custom password change template.
        form_class (Form): The form class used for password change.
        success_url (str): The URL to redirect to after a successful password
        change.
    """

    template_name = "customer_portal/user_password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("password_change_done")


def contact_us(request):
    """
    create a view for contact us
    """
    try:
        if request.method == "POST":
            form = ContactUsForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("contact_us")
            else:
                return render(
                    request, "customer_portal/contact_us.html", {"form": form}
                )
        else:
            form = ContactUsForm()
            return render(request, "customer_portal/contact_us.html", {"form": form})
    except Exception as e:
        return HttpResponse(str(e))


def subscribe_newsletter(request):
    if request.method == "POST":
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {"message": "You have subscribed successfully!"}, status=200
            )
        else:
            return JsonResponse(
                {"message": form.errors.get("email", ["An error occurred"])[0]},
                status=400,
            )
    return JsonResponse({"message": "Invalid request method."}, status=405)
