from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class UserAdmin(UserAdmin):
    model = User

    # Define the fields to be used in the user list view and detail view
    list_display = (
        "id",
        "date_joined",
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "gender",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "gender")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone_number", "gender")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "gender",
                    "password1",
                    "password2",
                    "groups",
                ),
            },
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)


admin.site.register(User, UserAdmin)
