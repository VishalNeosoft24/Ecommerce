from django.urls import path, include
from .authentication import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter
from .products.views import ProductViewSet


router = DefaultRouter()
router.register(r"products", ProductViewSet)


urlpatterns = [
    # Swagger
    path("schema/", SpectacularAPIView.as_view(), name="schema"),  # OpenAPI 3 schema
    path(
        "schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),  # Swagger UI
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),  # ReDoc UI
    # Authentication
    path("auth/login/", views.LoginAPIView.as_view(), name="api_login"),
    path("auth/logout/", views.LogoutAPIView.as_view(), name="api_logout"),
    path("auth/register/", views.RegisterAPIView.as_view(), name="api_register"),
    path("auth/profile/", views.ProfileAPIView.as_view(), name="api_profile"),
    path("csrf-token/", views.get_csrf_token, name="csrf_token"),
    path("", include(router.urls)),
]
