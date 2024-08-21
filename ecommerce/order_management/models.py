from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Address, Coupon


class PaymentGateway(models.Model):
    """
    Represents a payment gateway that handles transactions for orders.
    This model includes information about the gateway, its creator, and modification details.
    """

    name = models.CharField(
        max_length=255, unique=True, help_text="Name of the payment gateway."
    )
    created_by = models.ForeignKey(
        User,
        related_name="created_payment_gateway",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created the payment gateway.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the payment gateway was created.",
    )
    updated_by = models.ForeignKey(
        User,
        related_name="updated_payment_gateway",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who last modified the payment gateway.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the payment gateway was last modified.",
    )

    def __str__(self):
        return self.name


class UserOrder(models.Model):
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
    AWB_NO = models.CharField(
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
        max_length=1,
        choices=STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Status",
    )
    billing_address = models.ForeignKey(
        Address, related_name="billing_orders", null=True, on_delete=models.SET_NULL
    )
    shipping_address = models.ForeignKey(
        Address, related_name="shipping_orders", null=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    created_by = models.ForeignKey(
        User,
        related_name="user_order_create",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created the payment gateway.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the payment gateway was last modified.",
    )
    updated_by = models.ForeignKey(
        User,
        related_name="user_order_update",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who last modified the payment gateway.",
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
