from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse


def home_page(request):
    return render(request, "customer_portal/index.html")


def login_page(request):
    try:
        if request.method == "POST":
            # Retrieve form data
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()

            # Validate form data
            if not username or not password:
                messages.error(request, "Both username and password are required.")
                return render(request, "customer_portal/login.html")

            # Optional: Add additional validation for username and password
            if len(username) < 3:
                messages.error(request, "Username must be at least 3 characters long.")
                return render(request, "customer_portal/login.html")

            if len(password) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
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
