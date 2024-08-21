from django.contrib import admin
from .models import PaymentGateway, UserOrder


# Register your models here.
@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    )
    search_fields = ("name",)
    list_filter = ("created_by", "updated_by")
    ordering = ("-created_at",)


@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "grand_total",
        "shipping_method",
        "shipping_charges",
        "AWB_NO",
        "coupon",
        "payment_gateway",
        "transaction_id",
        "status",
        "billing_address",
        "shipping_address",
        "created_at",
        "updated_at",
    )
    search_fields = ("user__username", "AWB_NO", "transaction_id", "status")
    list_filter = (
        "status",
        "shipping_method",
        "coupon",
        "payment_gateway",
        "created_by",
        "updated_by",
    )
    ordering = ("-created_at",)
