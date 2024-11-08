from rest_framework import serializers
from product_management.models import (
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """ProductAttributeValueSerializer"""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = ProductAttributeValue
        fields = [
            "id",
            "attribute_value",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        attribute_value_instance = ProductAttributeValue.objects.create(
            **validated_data
        )
        return attribute_value_instance

    def update(self, instance, validated_data):
        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()
        return instance


class ProductAttributeSerializer(serializers.ModelSerializer):
    """ProductAttributeSerializer"""

    id = serializers.IntegerField(required=False)

    product_attribute_key = ProductAttributeValueSerializer(many=True)

    class Meta:
        model = ProductAttribute
        fields = [
            "id",
            "name",
            "product_attribute_key",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        attribute_values = validated_data.pop("product_attribute_key")

        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        attribute_instance = ProductAttribute.objects.create(**validated_data)

        for attribute_value_data in attribute_values:
            attribute_value_serializer = ProductAttributeValueSerializer(
                data=attribute_value_data,
                context=self.context,
            )
            if attribute_value_serializer.is_valid():
                attribute_value_serializer.save(product_attribute=attribute_instance)
        return attribute_instance

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            validated_data["updated_by"] = request.user

        attribute_values = validated_data.pop("product_attribute_key")

        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()

        existing_attributes = {
            attr.id: attr for attr in instance.product_attribute_key.all()
        }

        for attribute_value_data in attribute_values:
            attribute_value_id = attribute_value_data.get("id", None)
            if attribute_value_id and attribute_value_id in existing_attributes:
                attribute_value_instance = existing_attributes.pop(attribute_value_id)

                attribute_value_serializer = ProductAttributeValueSerializer(
                    attribute_value_instance,
                    data=attribute_value_data,
                    partial=True,
                )
                if attribute_value_serializer.is_valid():
                    attribute_value_serializer.save(product_attribute=instance)
            else:
                # Create new ProductAttribute if no id provided
                attribute_value_serializer = ProductAttributeValueSerializer(
                    data=attribute_value_data,
                    context=self.context,
                )
                if attribute_value_serializer.is_valid():
                    attribute_value_serializer.save(product_attribute=instance)

        for leftover in existing_attributes.values():
            leftover.delete()

        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    """ProductImageSerializer"""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
        ]


class ProductSerializer(serializers.ModelSerializer):
    """ProductSerializer"""

    product_attribute = ProductAttributeSerializer(many=True)
    # product_images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "quantity",
            "short_description",
            "long_description",
            "price",
            "product_attribute",
            # "product_images",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        attribute_data = validated_data.pop("product_attribute")
        product = Product.objects.create(**validated_data)

        for attribute in attribute_data:
            attribute_serializer = ProductAttributeSerializer(
                data=attribute, context=self.context
            )
            if attribute_serializer.is_valid():
                attribute_serializer.save(product=product)

        return product

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and hasattr(request, "user"):
            validated_data["updated_by"] = request.user

        attribute_data = validated_data.pop("product_attribute")

        for key, val in validated_data.items():
            setattr(instance, key, val)
        instance.save()

        existing_attributes = {
            attr.id: attr for attr in instance.product_attribute.all()
        }

        for attribute in attribute_data:
            attribute_name_id = attribute.get("id", None)
            if attribute_name_id and attribute_name_id in existing_attributes:

                attribute_instance = existing_attributes.pop(attribute_name_id)

                attribute_serializer = ProductAttributeSerializer(
                    attribute_instance,
                    data=attribute,
                    context=self.context,
                    partial=True,
                )
                if attribute_serializer.is_valid():
                    attribute_serializer.save()
            else:
                # Create new ProductAttribute if no id provided
                attribute_serializer = ProductAttributeSerializer(data=attribute_data)
                if attribute_serializer.is_valid():
                    attribute_serializer.save(
                        product_attribute=instance, context=self.context
                    )

        for leftover in existing_attributes.values():
            leftover.delete()

        return instance


class ProductListSerializer(serializers.ModelSerializer):
    """ProductListSerializer"""

    product_attribute = ProductAttributeSerializer(many=True)

    class Meta:
        model = Product
        fields = ["id", "name", "category", "price", "product_attribute"]
