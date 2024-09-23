from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)


# Register your models here.
class ProductAttributeValueInline(admin.StackedInline):
    model = ProductAttributeValue
    extra = 1


class ProductAttributeInline(admin.StackedInline):
    model = ProductAttribute
    extra = 1


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent", "description", "created_at", "updated_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    raw_id_fields = ("category",)
    list_display = [
        "id",
        "name",
        "short_description",
        "long_description",
        "price",
        "quantity",
        "is_active",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "deleted_at",
    ]
    inlines = [ProductAttributeInline, ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    raw_id_fields = ("product",)
    list_display = [
        "id",
        "image",
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
    inlines = [ProductAttributeValueInline]


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
