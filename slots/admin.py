from django.contrib import admin
from django.utils import timezone
from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'event', 'start_time', 'end_time',
        'capacity', 'booked_capacity_display', 'remaining_capacity_display',
        'is_blocked'
    ]
    search_fields = ['event__name', 'event__venue__name']
    list_filter = [
        'event', 'is_blocked', 'capacity',
        ('start_time', admin.DateFieldListFilter)
    ]
    ordering = ['start_time']
    list_per_page = 10
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = ['block_slots', 'unblock_slots', 'soft_delete_slots', 'restore_slots']

    def booked_capacity_display(self, obj):
        return obj.booked_capacity()
    booked_capacity_display.short_description = "Booked"

    def remaining_capacity_display(self, obj):
        return obj.remaining_capacity()
    remaining_capacity_display.short_description = "Available"

    # ------------------------------------------------
    # ✅ CONTROL MODULE VISIBILITY IN ADMIN DASHBOARD
    # ------------------------------------------------
    def has_module_permission(self, request):
        return check_role_permission(request.user, 'Slots', 'read')

    def has_view_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Slots', 'read')

    def has_add_permission(self, request):
        return check_role_permission(request.user, 'Slots', 'create')

    def has_change_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Slots', 'update')

    def has_delete_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Slots', 'delete')

    # ------------------------------------------------
    # ✅ BULK ACTIONS (Visible Only If Allowed)
    # ------------------------------------------------
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not check_role_permission(request.user, 'Slots', 'delete'):
            actions.pop('soft_delete_slots', None)
        if not check_role_permission(request.user, 'Slots', 'update'):
            actions.pop('restore_slots', None)
            actions.pop('block_slots', None)
            actions.pop('unblock_slots', None)
        return actions

    # ------------------------------------------------
    # ✅ CUSTOM ACTIONS
    # ------------------------------------------------
    def block_slots(self, request, queryset):
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f"{updated} slot(s) blocked.")
    block_slots.short_description = "Block selected slots"

    def unblock_slots(self, request, queryset):
        updated = queryset.update(is_blocked=False)
        self.message_user(request, f"{updated} slot(s) unblocked.")
    unblock_slots.short_description = "Unblock selected slots"

    def soft_delete_slots(self, request, queryset):
        updated = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{updated} slot(s) soft deleted.")
    soft_delete_slots.short_description = "Soft delete selected slots"

    def restore_slots(self, request, queryset):
        updated = queryset.update(deleted_at=None)
        self.message_user(request, f"{updated} slot(s) restored.")
    restore_slots.short_description = "Restore selected slots"
