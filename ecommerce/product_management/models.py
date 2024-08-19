from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    description = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="category_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="category_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        full_path = [self.name]
        p = self.parent
        while p is not None:
            full_path.append(p.name)
            p = p.parent
        return " -> ".join(full_path[::-1])


class Product(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField()
    price = models.FloatField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category"
    )
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.quantity}"

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        related_name="product_images",
        verbose_name="Product foreign key",
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_images_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_images_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)


class ProductAttribute(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_attribute"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_attribute_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_attribute_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class ProductAttributeValue(models.Model):
    product_attribute = models.ForeignKey(
        ProductAttribute, on_delete=models.CASCADE, related_name="product_attribute_key"
    )
    attribute_value = models.CharField(max_length=50)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_attribute_value_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_attribute_value_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.attribute_value}"
