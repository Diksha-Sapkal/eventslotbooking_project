# # users/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.utils.html import mark_safe
# from users.models import User, UserRole, RolePermission

# # -------------------------------
# # 1️⃣ UserRole Admin
# # -------------------------------
# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     # list_editable = ('name',) 
#     search_fields = ('name',)
#     list_filter = ()

# # -------------------------------
# # 2️⃣ RolePermission Admin
# # -------------------------------
# @admin.register(RolePermission)
# class RolePermissionAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete'
#     )
#     # list_editable = ('role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete')
#     list_filter = ('role', 'module_name', 'is_read', 'is_create', 'is_update', 'is_delete')
#     search_fields = ('role__name', 'module_name')

# # -------------------------------
# # 3️⃣ User Admin (Enhanced)
# # -------------------------------
# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     list_display = (
#         'id', 'username', 'email', 'first_name', 'last_name', 'role', 
#         'phone_no', 'city', 'state', 'pincode', 'is_staff', 'is_superuser', 'is_active', 'image_tag'
#     )
#     # list_editable = (
#     #     'username', 'email', 'first_name', 'last_name', 'role', 
#     #     'phone_no', 'city', 'state', 'pincode', 'is_staff', 'is_superuser', 'is_active'
#     # )
#     search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_no', 'city', 'state', 'pincode', 'role__name')
#     list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'city', 'state')

#     ordering = ('id',)

#     # Form me dikhenge
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_no', 'address', 'city', 'state', 'pincode', 'image', 'role')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#     )

#     # User create karte waqt
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'first_name', 'last_name', 'phone_no', 'address', 'city', 'state', 'pincode', 'role', 'password1', 'password2'),
#         }),
#     )

#     # -------------------------------
#     # Bulk Actions
#     # -------------------------------
#     actions = ['make_active', 'make_inactive']

#     def make_active(self, request, queryset):
#         updated = queryset.update(is_active=True)
#         self.message_user(request, f"{updated} user(s) marked as active.")
#     make_active.short_description = "Mark selected users as active"

#     def make_inactive(self, request, queryset):
#         updated = queryset.update(is_active=False)
#         self.message_user(request, f"{updated} user(s) marked as inactive.")
#     make_inactive.short_description = "Mark selected users as inactive"

#     # -------------------------------
#     # Image Thumbnail
#     # -------------------------------
#     def image_tag(self, obj):
#         if obj.image:
#             return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
#         return "-"
#     image_tag.short_description = 'Image'


# users/admin.py

# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from django import forms
from users.models import User, UserRole, RolePermission

# =====================================================
# 1️⃣ Custom User Change Form (Edit User)
# =====================================================
class CustomUserChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required and not field.label.endswith("*"):
                field.label = f"{field.label} *"

    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_no', 'city', 'state', 'pincode', 'role'
        ]
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")
        return cleaned_data


# =====================================================
# 2️⃣ Custom User Add Form (Add User)
# =====================================================
class CustomUserAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required and not field.label.endswith("*"):
                field.label = f"{field.label} *"

    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_no', 'city', 'state', 'pincode', 'role', 'password'
        ]
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_',' ').title()} is required.")
        return cleaned_data


# =====================================================
# 3️⃣ UserRole Admin
# =====================================================
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# =====================================================
# 4️⃣ RolePermission Admin
# =====================================================
@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'role', 'module_name',
        'is_read', 'is_create', 'is_update', 'is_delete'
    )
    list_filter = ('role', 'module_name')
    search_fields = ('role__name', 'module_name')


# =====================================================
# 5️⃣ User Admin
# =====================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserAddForm

    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'role',
        'phone_no', 'city', 'state', 'pincode',
        'is_staff', 'is_superuser', 'is_active', 'image_tag'
    )

    search_fields = (
        'username', 'email', 'first_name', 'last_name',
        'phone_no', 'city', 'state', 'pincode', 'role__name'
    )

    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('id',)

    # -------------------------------
    # Fieldsets (Edit User)
    # -------------------------------
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_no',
                'address', 'city', 'state', 'pincode', 'image', 'role'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
    )

    # -------------------------------
    # Fieldsets (Add User)
    # -------------------------------
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password',
                'email', 'first_name', 'last_name',
                'phone_no', 'address', 'city', 'state', 'pincode',
                'role'
            ),
        }),
    )

    # =====================================================
    # ⭐ Add * sign to ALL required fields in admin form
    # =====================================================
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if field.required and not field.label.endswith("*"):
                field.label = f"{field.label} *"
        return form

    # -------------------------------
    # Bulk Actions
    # -------------------------------
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated.")
    make_active.short_description = "Mark selected users active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")
    make_inactive.short_description = "Mark selected users inactive"

    # -------------------------------
    # Image Preview
    # -------------------------------
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "-"
    image_tag.short_description = 'Image'
