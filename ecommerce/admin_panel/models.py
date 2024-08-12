from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class ContactUs(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    note_admin = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} - {self.last_name} ({self.email})"


class Coupon(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    discount = models.FloatField()
    count = models.IntegerField(default=0, verbose_name="Coupon Used Count")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coupon_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coupon_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.code} ({self.discount})"

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class Address(models.Model):

    ADDRESS_CHOICES = [(0, "HOME"), (1, "WORK"), (2, "OTHER")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20, choices=ADDRESS_CHOICES, verbose_name="Address type"
    )
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    apartment_number = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    default = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name}: {self.user.last_name}, {self.state}, {self.country}"


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    cc = models.CharField(max_length=50, blank=True, null=True)
    bcc = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.save(using=using)


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="banners/")
    url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    last_modified = models.DateTimeField(auto_now=True)
    click_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class Category(models.Model):
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


class Product(models.Model):
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=100)
    long_description = models.TextField()
    price = models.FloatField()
    categories = models.ManyToManyField(Category, related_name="products")
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
        Product, on_delete=models.CASCADE, null=True, verbose_name="Product foreign key"
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
