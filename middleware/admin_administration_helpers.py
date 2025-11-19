# middleware/admin_administration_helpers.py
from users.models import RolePermission

def check_role_permission(user, module_name, action):
    """
    Check if a user has permission for a module in Django Admin.
    action: 'read', 'create', 'update', 'delete'
    """
    # Superuser or Superadmin → full access
    # if user.is_superuser or (
    #     getattr(user, 'role', None) and user.role.name.lower() == 'superadmin'
    # ):
    #     return True

    if not hasattr(user, 'role') or user.role is None:
        return False

    # Normalize module name (case-insensitive lookup)
    perm = RolePermission.objects.filter(
        role=user.role,
        module_name__iexact=module_name.strip()
    ).first()

    if not perm:
        return False

    action_map = {
        'read': perm.is_read,
        'create': perm.is_create,
        'update': perm.is_update,
        'delete': perm.is_delete,
    }

    return bool(action_map.get(action, False))
