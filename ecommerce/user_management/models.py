from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, blank=True, null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.username
