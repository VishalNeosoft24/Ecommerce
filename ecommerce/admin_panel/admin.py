from django.contrib import admin
from .models import (
    ContactUs,
    Coupon,
    Banner,
    Address,
    EmailTemplate,
    Banner,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)

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
        "name",
        "cc",
        "bcc",
        "subject",
        "body",
        "created_at",
        "updated_at",
        "deleted_at",
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent", "description", "created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "short_description",
        "long_description",
        "price",
        "category",
        "quantity",
        "is_active",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "deleted_at",
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "image",
        "product",
        "is_active",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "product",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product_attribute",
        "attribute_value",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    ]
