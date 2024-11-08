from rest_framework import viewsets, filters
from product_management.models import Product
from .serializers import ProductSerializer, ProductListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apis.filters import ProductFilter
from rest_framework.pagination import PageNumberPagination


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).all()
    serializer_class = ProductSerializer

    # Enable filters and search capabilities
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination

    search_fields = ["name"]
    ordering_fields = ["price"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return super().get_serializer_class()
