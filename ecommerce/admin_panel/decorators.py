from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def check_user_permission(permission_codename, type=None):

    def decorator(func):
        @wraps(func)
        @login_required(login_url="login")
        def inner(request, *args, **kwargs):
            is_check = request.GET.get("is_check", None)

            # Check if the user has the required permission
            has_permission = request.user.has_perm(permission_codename)

            if is_check:
                if request.user.is_superuser or has_permission:
                    return JsonResponse({"status": "success", "code": 1})
                else:
                    return JsonResponse({"status": "error", "code": 0})
            if request.user.is_superuser or has_permission:
                result = func(request, *args, **kwargs)
                return result
            else:
                if type == "api":
                    return JsonResponse({"status": "error", "msg": "Permission Denied"})
                else:
                    return render(
                        request, "admin_panel/404.html"
                    )  # Raise Http404 for non-API requests

        return inner

    return decorator
