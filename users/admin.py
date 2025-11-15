# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from users.models import User, UserRole, RolePermission

# -------------------------------
# 1️⃣ UserRole Admin
# -------------------------------
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    # list_editable = ('name',) 
    search_fields = ('name',)
    list_filter = ()

# -------------------------------
# 2️⃣ RolePermission Admin
# -------------------------------
@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete'
    )
    # list_editable = ('role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete')
    list_filter = ('role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete')
    search_fields = ('role__name', 'module_name')

# -------------------------------
# 3️⃣ User Admin (Enhanced)
# -------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'role', 
        'phone_no', 'city', 'state', 'pincode', 'is_staff', 'is_superuser', 'is_active', 'image_tag'
    )
    # list_editable = (
    #     'username', 'email', 'first_name', 'last_name', 'role', 
    #     'phone_no', 'city', 'state', 'pincode', 'is_staff', 'is_superuser', 'is_active'
    # )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_no', 'city', 'state', 'pincode', 'role__name')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'city', 'state')

    ordering = ('id',)

    # Form me dikhenge
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_no', 'address', 'city', 'state', 'pincode', 'image', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # User create karte waqt
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_no', 'address', 'city', 'state', 'pincode', 'role', 'password1', 'password2'),
        }),
    )

    # -------------------------------
    # Bulk Actions
    # -------------------------------
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) marked as active.")
    make_active.short_description = "Mark selected users as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) marked as inactive.")
    make_inactive.short_description = "Mark selected users as inactive"

    # -------------------------------
    # Image Thumbnail
    # -------------------------------
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "-"
    image_tag.short_description = 'Image'
