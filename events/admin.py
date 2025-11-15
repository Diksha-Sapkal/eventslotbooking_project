from django.contrib import admin
from django.utils import timezone
from events.models.event_model import Event
from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission



class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1  # Number of empty slots to show by default
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    fields = ['start_time', 'end_time', 'capacity', 'is_blocked', 'created_at', 'updated_at']
    can_delete = True
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'venue', 'description', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'venue__name']
    list_filter = ['venue', 'start_date', 'end_date']
    ordering = ['start_date']
    list_per_page = 10
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = ['soft_delete_events', 'restore_events']

    # Add the inline here
    inlines = [SlotInline]

    # ---------------- Permission Controls ----------------
    def has_module_permission(self, request):
        return check_role_permission(request.user, 'Events', 'read')

    def has_view_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Events', 'read')

    def has_add_permission(self, request):
        return check_role_permission(request.user, 'Events', 'create')

    def has_change_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Events', 'update')

    def has_delete_permission(self, request, obj=None):
        return check_role_permission(request.user, 'Events', 'delete')

    # ---------------- Bulk Actions ----------------
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not check_role_permission(request.user, 'Events', 'delete'):
            actions.pop('soft_delete_events', None)
        if not check_role_permission(request.user, 'Events', 'update'):
            actions.pop('restore_events', None)
        return actions

    # ---------------- Soft Delete / Restore ----------------
    def soft_delete_events(self, request, queryset):
        updated = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{updated} event(s) soft deleted.")
    soft_delete_events.short_description = "Soft delete selected events"

    def restore_events(self, request, queryset):
        updated = queryset.update(deleted_at=None)
        self.message_user(request, f"{updated} event(s) restored.")
    restore_events.short_description = "Restore selected events"

