from django.db import models
from django.utils import timezone
from user_management.models import User
from admin_panel.models import BaseModel


# Create your models here.
class Category(BaseModel):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    description = models.TextField()

    def __str__(self):
        full_path = [self.name]
        p = self.parent
        while p is not None:
            full_path.append(p.name)
            p = p.parent
        return " -> ".join(full_path[::-1])


class Product(BaseModel):
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField()
    price = models.FloatField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category"
    )
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.quantity}"

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class ProductImage(BaseModel):
    image = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        related_name="product_images",
        verbose_name="Product foreign key",
    )
    is_active = models.BooleanField(default=True)


class ProductAttribute(BaseModel):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_attribute"
    )

    def __str__(self):
        return f"{self.name}"


class ProductAttributeValue(BaseModel):
    product_attribute = models.ForeignKey(
        ProductAttribute, on_delete=models.CASCADE, related_name="product_attribute_key"
    )
    attribute_value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute_value}"
