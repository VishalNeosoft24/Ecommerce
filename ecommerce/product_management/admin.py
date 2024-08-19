from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)

# Register your models here.


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
