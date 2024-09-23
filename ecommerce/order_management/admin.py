from django.contrib import admin
from .models import PaymentGateway, UserOrder, OrderDetail, UserWishList


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


class OrderDetailInline(admin.StackedInline):
    model = OrderDetail
    extra = 1


@admin.register(UserOrder)
class UserOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "grand_total",
        "shipping_method",
        "shipping_charges",
        "awb_no",
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
    inlines = [OrderDetailInline]


@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "amount",
        "created_at",
        "updated_at",
    )


@admin.register(UserWishList)
class UserWishListAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "product")
