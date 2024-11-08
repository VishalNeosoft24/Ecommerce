import django_filters
from product_management.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Minimum Price"
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Maximum Price"
    )
    attribute_value = django_filters.CharFilter(
        field_name="product_attribute__name",
        lookup_expr="icontains",
        label="Attribute Name",
    )

    attribute_value_key = django_filters.CharFilter(
        field_name="product_attribute__product_attribute_key__attribute_value",
        lookup_expr="icontains",
        label="Attribute Value Name",
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "min_price",
            "max_price",
            "attribute_value",
            "attribute_value_key",
        ]
