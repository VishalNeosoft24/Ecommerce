from django.utils import timezone
from django.db import models
from user_management.models import User


# Create your models here.
class BaseModel(models.Model):

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_updated"
    )
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


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


class Coupon(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    description = models.TextField()
    discount = models.FloatField()
    count = models.IntegerField(default=0, verbose_name="Coupon Used Count")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.name}"

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class Address(BaseModel):

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

    def save(self, *args, **kwargs):
        if self.default:
            Address.objects.filter(user=self.user).update(default=False)
        super(Address, self).save(*args, **kwargs)

    def __str__(self):
        address_parts = [
            f"{self.street_address}",
            f"Apt {self.apartment_number}" if self.apartment_number else "",
            f"{self.city}, {self.state}",
            f"{self.pincode}",
            f"{self.country}",
        ]
        return f"{', '.join(part for part in address_parts if part)}"


class EmailTemplate(BaseModel):
    title = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title


class Banner(BaseModel):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="banners/")
    url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        """Ordering"""

        ordering = ["display_order", "-updated_at", "id"]

    def __str__(self):
        return self.title

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete the instance by setting deleted_at to the current timestamp.
        """
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(using=using)


class CMS(BaseModel):
    title = models.CharField(max_length=50)
    content = models.TextField()
    meta_title = models.TextField()
    meta_description = models.TextField()
    meta_keyword = models.TextField()

    def __str__(self):
        return f"{self.title}"


class NewsLetter(models.Model):
    """NewsLetter Model"""

    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmailLogs(models.Model):
    """Email Logs model"""

    email_template = models.ForeignKey(
        EmailTemplate, blank=True, null=True, on_delete=models.SET_NULL
    )
    to = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderStatusLogs(models.Model):
    """Order status logs"""

    from order_management.models import UserOrder

    order = models.ForeignKey(
        UserOrder, on_delete=models.DO_NOTHING, verbose_name="User Order"
    )
    status = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
