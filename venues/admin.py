from django.contrib import admin
from django.utils import timezone
from venues.models import Venue
from middleware.admin_administration_helpers import check_role_permission


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'city', 'state', 'pincode', 'capacity')
    search_fields = ('name', 'address', 'city', 'state', 'pincode')
    list_filter = ('city', 'state', 'capacity')
    ordering = ('id',)
    list_per_page = 10
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    actions = ['soft_delete_venues', 'restore_venues']

    # ------------------------------------------------
    # ✅ CONTROL MODULE VISIBILITY IN ADMIN DASHBOARD
    # ------------------------------------------------
    def has_module_permission(self, request):
        # Only show 'Venues' if user has READ permission
        return check_role_permission(request.user, 'Venues', 'read')

    def has_view_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Venues', 'read')

    def has_add_permission(self, request):
        return check_role_permission(request.user, 'Venues', 'create')

    def has_change_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Venues', 'update')

    def has_delete_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Venues', 'delete')

    # ------------------------------------------------
    # ✅ BULK ACTIONS (Visible Only If Allowed)
    # ------------------------------------------------
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not check_role_permission(request.user, 'Venues', 'delete'):
            actions.pop('soft_delete_venues', None)
        if not check_role_permission(request.user, 'Venues', 'update'):
            actions.pop('restore_venues', None)
        return actions

    # ------------------------------------------------
    # ✅ SOFT DELETE / RESTORE
    # ------------------------------------------------
    def soft_delete_venues(self, request, queryset):
        updated = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{updated} venue(s) soft deleted.")
    soft_delete_venues.short_description = "Soft delete selected venues"

    def restore_venues(self, request, queryset):
        updated = queryset.update(deleted_at=None)
        self.message_user(request, f"{updated} venue(s) restored.")
    restore_venues.short_description = "Restore selected venues"
