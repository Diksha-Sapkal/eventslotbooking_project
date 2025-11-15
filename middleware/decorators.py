from functools import wraps
from django.http import JsonResponse

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'message': 'Authentication required'}, status=401)
            if user.role not in allowed_roles:
                return JsonResponse({'message': 'Access denied'}, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
