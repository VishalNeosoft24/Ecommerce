from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    path("register/", views.register_page, name="register_page"),
    path("login/", views.login_page, name="login_page"),
    path("logout/", views.logout_page, name="logout_page"),
    path("profile/", views.profile_page, name="profile_page"),
    path("update-user/<int:id>", views.update_user, name="update_user"),
    path("add-address/", views.add_address, name="add_address"),
    path("update-address/<int:id>", views.update_address, name="update_address"),
    path("delete-address/<int:id>", views.delete_address, name="delete_address"),
    path(
        "change-password/",
        views.CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
    path(
        "password-change/done/",
        TemplateView.as_view(template_name="customer_portal/password_change_done.html"),
        name="password_change_done",
    ),
    # Password reset URLs
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # contact Us
    path("contact-us/", views.contact_us, name="contact_us"),
]
