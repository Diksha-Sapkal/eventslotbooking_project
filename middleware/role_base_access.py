# employee/middleware/role_base_access.py
from django.http import JsonResponse
from users.models import RolePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        path = request.path

        # Bypass for admin, swagger, auth/register, auth/login
        if any(p in path for p in ['admin', 'swagger', 'auth/register', 'auth/login']):
            return self.get_response(request)

        # ✅ Direct token authentication
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'message': 'Authentication required'}, status=401)

        try:
            validated_token = self.jwt_auth.get_validated_token(token)
            request.user = self.jwt_auth.get_user(validated_token)
        except Exception:
            return JsonResponse({'message': 'Invalid or expired token'}, status=401)

        # ✅ Role check
        if not getattr(request.user, 'role', None):
            return JsonResponse({'message': 'No role assigned'}, status=403)

        # ✅ Module & CRUD permission check
        parts = path.strip('/').split('/')
        module_name = parts[1].capitalize() if len(parts) > 1 else parts[0].capitalize()
        try:
            permission = RolePermission.objects.get(role=request.user.role, module_name=module_name)
        except RolePermission.DoesNotExist:
            return JsonResponse({'message': f'Access denied for module {module_name}'}, status=403)

        method = request.method
        allowed = (
            (method == 'GET' and permission.is_read) or
            (method == 'POST' and permission.is_create) or
            (method in ['PUT', 'PATCH'] and permission.is_update) or
            (method == 'DELETE' and permission.is_delete)
        )
        if not allowed:
            return JsonResponse({'message': f'{method} not allowed for your role'}, status=403)

        return self.get_response(request)
