from rest_framework import serializers
from django.contrib.auth import authenticate

from user_management.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(write_only=True)  # Set password as write-only

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "email"]

    def create(self, validated_data):
        # Remove password from validated_data before creating the user instance
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """LoginSerializer"""

    username = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            "blank": "Username cannot be blank.",
            "required": "Username is required.",
        },
    )
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        error_messages={
            "blank": "Password cannot be blank.",
            "required": "Password is required.",
        },
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        attrs["user"] = user
        return attrs
