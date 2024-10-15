# Standard Django imports
from django.db import models
from django.utils import timezone

# App-specific imports
from admin_panel.models import Address, Coupon, BaseModel
from product_management.models import Product
from user_management.models import User
from django.db.models import Sum


class PaymentGateway(BaseModel):
    """
    Represents a payment gateway that handles transactions for orders.
    This model includes information about the gateway, its creator, and modification details.
    """

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    def __str__(self):
        return self.name


class UserOrder(BaseModel):
    """
    Represents an order placed by a user with various details.
    """

    SHIPPING_METHOD_CHOICES = [
        ("STD", "Standard Shipping"),
        ("EXP", "Express Shipping"),
        ("OVN", "Overnight Shipping"),
        ("PUP", "In-Store Pickup"),
    ]

    STATUS_CHOICES = [
        ("P", "Pending"),
        ("O", "Processing"),
        ("S", "Shipped"),
        ("D", "Delivered"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("P", "Pending"),
        ("S", "Successful"),
        ("F", "Failed"),
        ("C", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, related_name="orders", on_delete=models.CASCADE, verbose_name="User"
    )
    grand_total = models.DecimalField(
        null=True,
        verbose_name="Grand Total",
        max_digits=12,
        decimal_places=2,
    )
    shipping_method = models.CharField(
        max_length=3,
        choices=SHIPPING_METHOD_CHOICES,
        default="STD",
        verbose_name="Shipping Method",
    )
    shipping_charges = models.DecimalField(
        null=True, verbose_name="Shipping Charges", max_digits=12, decimal_places=2
    )
    awb_no = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="AWB Number"
    )
    coupon = models.ForeignKey(
        Coupon,
        related_name="user_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Coupon",
    )
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICES,
        default="P",
        verbose_name="Payment Status",
    )
    payment_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Payment ID"
    )
    payment_gateway = models.ForeignKey(
        PaymentGateway,
        related_name="user_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Payment Gateway",
    )
    transaction_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Transaction ID"
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, verbose_name="Status", default="P"
    )
    billing_address = models.ForeignKey(
        Address,
        related_name="billing_orders",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Billing Address",
    )
    shipping_address = models.ForeignKey(
        Address,
        related_name="shipping_orders",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Shipping Address",
    )

    class Meta:
        ordering = ["-created_at"]

    def generate_awb_no(self):
        """Generate AWB number using current timestamp and shipping method."""
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        method = self.shipping_method
        return f"ORD{timestamp}{method}"

    def save(self, *args, **kwargs):
        """Override save method to set awb_no before saving the instance."""
        if not self.awb_no:
            self.awb_no = self.generate_awb_no()
        self.created_by = self.user
        self.updated_by = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_sub_total(self):
        sub_total = OrderDetail.objects.filter(order=self).aggregate(
            sub_total=Sum("amount")
        )
        return float(sub_total["sub_total"] or 0)

    def get_discount_amount(self):
        """Calculate the discount amount."""
        if self.coupon:
            sub_total = self.get_sub_total()
            # Assuming `self.coupon.discount_percentage` exists
            discount_amount = sub_total * (self.coupon.discount / 100)
            return discount_amount
        return 0

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, "")


class OrderDetail(BaseModel):
    """
    Represents the details of an order, including products and quantities.
    """

    order = models.ForeignKey(
        UserOrder,
        on_delete=models.SET_NULL,
        related_name="order_details",
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="order_details",
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - Product {self.product.name}"

    def save(self, *args, **kwargs):
        """Override save method"""
        self.created_by = self.order.user
        self.updated_by = self.order.user
        super().save(*args, **kwargs)


class UserWishList(BaseModel):
    user = models.ForeignKey(
        User, related_name="user_wishlist", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="wishlist_product", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.product.name

    def save(self, *args, **kwargs):
        """Override save method to set awb_no before saving the instance."""
        self.created_by = self.user
        self.updated_by = self.user
        super().save(*args, **kwargs)


class PaymentLogs(models.Model):
    """webhook response data"""

    pay_ord_id = models.CharField(max_length=50, verbose_name="Payment Order Id")
    pay_status = models.CharField(max_length=50, verbose_name="Payment Status")
    response_dict = models.TextField(verbose_name="Response In Str Form")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
