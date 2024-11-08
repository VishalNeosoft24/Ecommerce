from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    LoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from django.contrib.auth import login, logout
from django.views.decorators.csrf import ensure_csrf_cookie


class RegisterAPIView(APIView):
    """User Registration"""

    permission_classes = [AllowAny]

    def post(self, request):
        """post request"""

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"success": True, "message": "User Created Successfully"}
            )
        else:
            return JsonResponse({"status": False, "message": serializer.errors})


class LoginAPIView(APIView):
    """login api using DRF"""

    permission_classes = [AllowAny]

    def post(self, request):
        """user login"""

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user is not None:
                login(request, user)
                return JsonResponse(
                    {"success": True, "message": "Login Successful"},
                )
            else:
                return JsonResponse(
                    {"success": False, "message": "Invalid Credentials"},
                )
        else:
            return JsonResponse(
                {"success": False, "message": serializer.errors},
            )


class LogoutAPIView(APIView):
    """logout view"""

    def post(self, request):
        try:
            logout(request=request)
            return JsonResponse({"success": True, "message": "Logout Successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


class ProfileAPIView(APIView):
    """User Profile"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return JsonResponse(serializer.data)

    def put(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {
                    "success": True,
                    "message": "User Updated Successfully",
                    "data": serializer.data,
                }
            )
        else:
            return JsonResponse(
                {"success": False, "message": serializer.errors},
            )


@ensure_csrf_cookie
def get_csrf_token(request):
    """get csrf token"""
    return JsonResponse({"csrfToken": request.META.get("CSRF_COOKIE", "")})
