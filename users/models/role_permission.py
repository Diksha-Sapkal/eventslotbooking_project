from django.db import models
from .user_role import UserRole

class RolePermission(models.Model):
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    module_name = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    is_create = models.BooleanField(default=False)
    is_update = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'role_permission'
        unique_together = ('role', 'module_name')

    def __str__(self):
        return f"{self.role} - {self.module_name}"
