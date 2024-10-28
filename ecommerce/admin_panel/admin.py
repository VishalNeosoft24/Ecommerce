from django.contrib import admin
from .models import (
    ContactUs,
    Coupon,
    Banner,
    Address,
    EmailTemplate,
    NewsLetter,
    UserEventTracking,
)
from django.contrib.auth.models import Permission


# Register your models here.


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "type",
        "country",
        "state",
        "city",
        "pincode",
        "street_address",
        "apartment_number",
        "phone_number",
        "active",
        "default",
    ]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "image",
        "url",
        "is_active",
        "status",
        "display_order",
        "created_at",
        "updated_at",
        "deleted_at",
    ]


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "message",
        "created_at",
    ]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "code",
        "name",
        "count",
        "is_active",
        "description",
        "discount",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "deleted_at",
    ]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "subject",
        "content",
        "created_at",
        "updated_at",
        "deleted_at",
    ]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "codename")
    search_fields = ("name", "codename")


@admin.register(NewsLetter)
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "created_at"]
    search_fields = ("email",)


@admin.register(UserEventTracking)
class UserEventTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "requested_url",
        "object_info",
        "event_type",
        "event_time",
        "event_metadata",
        "session_id",
        "ip_address",
        "device_type",
        "browser_info",
        "location",
    )
    search_fields = ("user__username", "event_type", "ip_address", "session_id")
    list_filter = ("event_type", "device_type", "event_time", "user")
    ordering = ("-event_time",)  # Order by event_time descending
