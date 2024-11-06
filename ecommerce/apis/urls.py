from django.urls import path
from .authentication import views

urlpatterns = [
    # Authentication
    path("auth/login/", views.LoginAPIView.as_view(), name="api_login"),
    path("auth/logout/", views.LogoutAPIView.as_view(), name="api_logout"),
    path("auth/register/", views.RegisterAPIView.as_view(), name="api_register"),
    # path("auth/profile/", views.ProfileAPIView.as_view(), name="api_profile"),
    path("csrf-token/", views.get_csrf_token, name="csrf_token"),
]
