# FILE: slots/admin.py

from django.contrib import admin
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import path

from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


# -------------------------
# Slot Admin Form
# -------------------------
class SlotAdminForm(forms.ModelForm):

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Slot
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        now = timezone.now()
        s = cleaned.get("start_time")
        e = cleaned.get("end_time")

        if s and s < now:
            raise ValidationError("Start time cannot be in the past.")
        if e and e < now:
            raise ValidationError("End time cannot be in the past.")
        if s and e and e <= s:
            raise ValidationError("End time must be after start time.")

        return cleaned


# -------------------------
# Admin Actions
# -------------------------
@admin.action(description="Block selected slots")
def block_slots(modeladmin, request, queryset):
    queryset.update(is_blocked=True)


@admin.action(description="Unblock selected slots")
def unblock_slots(modeladmin, request, queryset):
    queryset.update(is_blocked=False)


@admin.action(description="Soft delete selected slots")
def soft_delete_slots(modeladmin, request, queryset):
    queryset.update(deleted_at=timezone.now())


@admin.action(description="Restore selected slots")
def restore_slots(modeladmin, request, queryset):
    queryset.update(deleted_at=None)


# -------------------------
# Slot Admin
# -------------------------
@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm

    list_display = [
        'sr_no', 'event', 'start_time', 'end_time',
        'capacity', 'booked_capacity_display',
        'remaining_capacity_display', 'is_blocked'
    ]

    list_filter = ("event", "is_blocked", "deleted_at")
    search_fields = ['event__name', 'event__venue__name']
    ordering = ['-id']
    list_per_page = 10

    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = [block_slots, unblock_slots, soft_delete_slots, restore_slots]

    class Media:
        js = ('js/filter_slots_dynamic.js',)    # <-- IMPORTANT (you must add this)
        css = {'all': ('css/clear_errors.css',)}

    # -------------------------
    # Needed for Sr No
    # -------------------------
    def get_queryset(self, request):
        self.request = request
        return super().get_queryset(request)

    def sr_no(self, obj):
        queryset = self.get_queryset(self.request)
        page = int(self.request.GET.get("p", 1))
        index = list(queryset.values_list('pk', flat=True)).index(obj.pk)
        return (page - 1) * self.list_per_page + index + 1

    sr_no.short_description = "Sr No"

    # -------------------------
    # Extra admin URL for AJAX
    # -------------------------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("get-slots/", self.admin_site.admin_view(self.get_slots), name="get-slots"),
        ]
        return custom + urls

    # -------------------------
    # AJAX Endpoint → Returns filtered slots
    # -------------------------
    def get_slots(self, request):
        event_id = request.GET.get("event_id")

        slots = Slot.objects.filter(
            event_id=event_id,
            deleted_at__isnull=True,
            is_blocked=False

        ).order_by("start_time")

        return JsonResponse({
            "slots": [
                {"id": s.id, "label": f"{s.start_time} → {s.end_time}"}
                for s in slots
            ]
        })

    # -------------------------
    # Capacity displays
    # -------------------------
    def booked_capacity_display(self, obj):
        return obj.booked_capacity()

    def remaining_capacity_display(self, obj):
        return obj.remaining_capacity()

    # -------------------------
    # Permissions
    # -------------------------
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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not check_role_permission(request.user, 'Slots', 'update'):
            actions.pop('block_slots', None)
            actions.pop('unblock_slots', None)
            actions.pop('restore_slots', None)
        if not check_role_permission(request.user, 'Slots', 'delete'):
            actions.pop('soft_delete_slots', None)
        return actions
