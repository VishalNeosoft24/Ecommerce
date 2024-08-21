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

    ADDRESS_CHOICES = [
        ("HOME", "Home"),
        ("WORK", "Work"),
        ("OTHER", "Other"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20,
        choices=ADDRESS_CHOICES,
        verbose_name="Address type",
        default="HOME",
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
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="emailtemplate_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="emailtemplate_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Banner(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="banners/")
    url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="banner_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="banner_updated"
    )
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


class cms(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    meta_title = models.TextField()
    meta_description = models.TextField()
    meta_keyword = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cms_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cms_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"
