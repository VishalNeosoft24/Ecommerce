from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse


def check_user_group(group_list=[]):
    def decorator(func):
        @wraps(func)
        @login_required(login_url="login")
        def inner(request, *args, **kwargs):
            is_check = request.GET.get("is_check", None)
            user_roles = request.user.groups.values_list("name", flat=True)
            if is_check:
                if request.user.is_superuser or any(
                    role in user_roles for role in group_list
                ):
                    return JsonResponse({"status": "success", "code": 1})
                else:
                    return JsonResponse({"status": "error", "code": 0})

            if request.user.is_superuser or any(
                role in user_roles for role in group_list
            ):
                result = func(request, *args, **kwargs)
                return result
            else:
                return JsonResponse({"status": "error", "msg": "Permission Denied"})

        return inner

    return decorator
