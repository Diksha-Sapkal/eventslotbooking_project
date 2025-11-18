# from django.contrib import admin
# from django import forms
# from django.utils import timezone
# from django.core.exceptions import ValidationError
# from slots.models.slot_model import Slot
# from middleware.admin_administration_helpers import check_role_permission


# class SlotAdminForm(forms.ModelForm):
#     """Custom form to show * for mandatory fields and prevent past dates"""
#     start_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
#         }),
#         input_formats=['%Y-%m-%dT%H:%M'],
#     )
#     end_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={
#             'type': 'datetime-local',
#             'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
#         }),
#         input_formats=['%Y-%m-%dT%H:%M'],
#     )

#     class Meta:
#         model = Slot
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add * to mandatory field labels
#         mandatory_fields = ['event', 'start_time', 'end_time', 'capacity']
#         for field_name in mandatory_fields:
#             if field_name in self.fields:
#                 self.fields[field_name].label = f"{self.fields[field_name].label} *"

#     def clean(self):
#         cleaned_data = super().clean()
#         now = timezone.now()
#         start_time = cleaned_data.get('start_time')
#         end_time = cleaned_data.get('end_time')

#         # Validate start_time is not in the past
#         if start_time and start_time < now:
#             raise ValidationError("Start time cannot be in the past.")

#         # Validate end_time is not in the past
#         if end_time and end_time < now:
#             raise ValidationError("End time cannot be in the past.")

#         # Validate end_time is after start_time
#         if start_time and end_time:
#             if end_time <= start_time:
#                 raise ValidationError("End time must be after start time.")

#         return cleaned_data


# @admin.register(Slot)
# class SlotAdmin(admin.ModelAdmin):
#     form = SlotAdminForm
#     list_display = [
#         'sr_no', 'event', 'start_time', 'end_time',
#         'capacity', 'booked_capacity_display', 'remaining_capacity_display',
#         'is_blocked'
#     ]
#     search_fields = ['event__name', 'event__venue__name']
#     list_filter = [
#         'event', 'is_blocked', 'capacity',
#         ('start_time', admin.DateFieldListFilter)
#     ]
#     ordering = ['-id']
#     list_per_page = 10
#     readonly_fields = ['created_at', 'updated_at', 'deleted_at']
#     actions = ['block_slots', 'unblock_slots', 'soft_delete_slots', 'restore_slots']
    
#     class Media:
#         css = {
#             'all': ('css/clear_errors.css',)
#         }
#         js = (
#             'js/restrict_past_dates.js',
#             'js/clear_field_errors.js',
#         )

#     def changelist_view(self, request, extra_context=None):
#         self.request = request
#         return super().changelist_view(request, extra_context)

#     def sr_no(self, obj):
#         """Display serialized Sr No instead of database ID"""
#         queryset = self.get_queryset(self.request)
#    def booked_capacity_display(self, obj):
#         return obj.booked_capacity()
#     booked_capacity_display.short_description = "Booked"

#     def remaining_capacity_display(self, obj):
#         return obj.remaining_capacity()
#     remaining_capacity_display.short_description = "Available"     page_num = int(self.request.GET.get('p', 1))
#         start_index = (page_num - 1) * self.list_per_page + 1
#         current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
#         return (page_num - 1) * self.list_per_page + current_index
#     sr_no.short_description = "Sr No"

#     

#     def save_model(self, request, obj, form, change):
#         """Validate that start_time and end_time are not in the past"""
#         now = timezone.now()
        
#         if obj.start_time < now:
#             self.message_user(request, "Error: Start time cannot be in the past.", level='error')
#             return
        
#         if obj.end_time < now:
#             self.message_user(request, "Error: End time cannot be in the past.", level='error')
#             return
        
#         if obj.end_time <= obj.start_time:
#             self.message_user(request, "Error: End time must be after start time.", level='error')
#             return
        
#         super().save_model(request, obj, form, change)

#     # ------------------------------------------------
#     # ✅ CONTROL MODULE VISIBILITY IN ADMIN DASHBOARD
#     # ------------------------------------------------
#     def has_module_permission(self, request):
#         return check_role_permission(request.user, 'Slots', 'read')

#     def has_view_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Slots', 'read')

#     def has_add_permission(self, request):
#         return check_role_permission(request.user, 'Slots', 'create')

#     def has_change_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Slots', 'update')

#     def has_delete_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Slots', 'delete')

#     # ------------------------------------------------
#     # ✅ BULK ACTIONS (Visible Only If Allowed)
#     # ------------------------------------------------
#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if not check_role_permission(request.user, 'Slots', 'delete'):
#             actions.pop('soft_delete_slots', None)
#         if not check_role_permission(request.user, 'Slots', 'update'):
#             actions.pop('restore_slots', None)
#             actions.pop('block_slots', None)
#             actions.pop('unblock_slots', None)
#         return actions

#     # ------------------------------------------------
#     # ✅ CUSTOM ACTIONS
#     # ------------------------------------------------
#     def block_slots(self, request, queryset):
#         updated = queryset.update(is_blocked=True)
#         self.message_user(request, f"{updated} slot(s) blocked.")
#     block_slots.short_description = "Block selected slots"

#     def unblock_slots(self, request, queryset):
#         updated = queryset.update(is_blocked=False)
#         self.message_user(request, f"{updated} slot(s) unblocked.")
#     unblock_slots.short_description = "Unblock selected slots"

#     def soft_delete_slots(self, request, queryset):
#         updated = queryset.update(deleted_at=timezone.now())
#         self.message_user(request, f"{updated} slot(s) soft deleted.")
#     soft_delete_slots.short_description = "Soft delete selected slots"

#     def restore_slots(self, request, queryset):
#         updated = queryset.update(deleted_at=None)
#         self.message_user(request, f"{updated} slot(s) restored.")
#     restore_slots.short_description = "Restore selected slots"

# slots/admin.py
from django.contrib import admin
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from slots.models import Slot


# -------------------------
# Slot Admin Form
# -------------------------
class SlotAdminForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields with asterisk in label
        mandatory_fields = ['event', 'start_time', 'end_time', 'capacity']
        for field_name in mandatory_fields:
            if field_name in self.fields:
                label = self.fields[field_name].label or field_name.replace('_', ' ').title()
                self.fields[field_name].label = f"{label} *"

    def clean(self):
        cleaned = super().clean()
        try:
            instance = self.instance
            for k, v in cleaned.items():
                setattr(instance, k, v)
            instance.clean()
        except ValidationError as e:
            raise forms.ValidationError(e.message_dict or e.messages)
        return cleaned


# -------------------------
# Admin Actions
# -------------------------
@admin.action(description="Block selected slots")
def block_slots(modeladmin, request, queryset):
    updated = queryset.update(is_blocked=True)
    modeladmin.message_user(request, f"{updated} slot(s) blocked.")


@admin.action(description="Unblock selected slots")
def unblock_slots(modeladmin, request, queryset):
    updated = queryset.update(is_blocked=False)
    modeladmin.message_user(request, f"{updated} slot(s) unblocked.")


@admin.action(description="Soft delete selected slots")
def soft_delete_slots(modeladmin, request, queryset):
    updated = queryset.update(deleted_at=timezone.now())
    modeladmin.message_user(request, f"{updated} slot(s) soft deleted.")


@admin.action(description="Restore selected slots")
def restore_slots(modeladmin, request, queryset):
    updated = queryset.update(deleted_at=None)
    modeladmin.message_user(request, f"{updated} slot(s) restored.")


# -------------------------
# Slot Admin
# -------------------------

from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


class SlotAdminForm(forms.ModelForm):
    """Custom form to show * for mandatory fields and prevent past dates"""
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Slot
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add * to mandatory field labels
        mandatory_fields = ['event', 'start_time', 'end_time', 'capacity']
        for field_name in mandatory_fields:
            if field_name in self.fields:
                self.fields[field_name].label = f"{self.fields[field_name].label} *"

    def clean(self):
        cleaned_data = super().clean()
        now = timezone.now()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Validate start_time is not in the past
        if start_time and start_time < now:
            raise ValidationError("Start time cannot be in the past.")

        # Validate end_time is not in the past
        if end_time and end_time < now:
            raise ValidationError("End time cannot be in the past.")

        # Validate end_time is after start_time
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")

        return cleaned_data



@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm
    list_display = [
        'sr_no', 'event', 'start_time', 'end_time',
        'capacity', 'booked_capacity_display', 'remaining_capacity_display',
        'is_blocked'
    ]

    list_filter = ("event", "is_blocked", "deleted_at")
    search_fields = ("event__name", "event__title")
    actions = [block_slots, unblock_slots, soft_delete_slots, restore_slots]
    readonly_fields = ['created_at', 'updated_at']

    search_fields = ['event__name', 'event__venue__name']
    list_filter = [
        'event', 'is_blocked', 'capacity',
        ('start_time', admin.DateFieldListFilter)
    ]
    ordering = ['-id']
    list_per_page = 10
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = ['block_slots', 'unblock_slots', 'soft_delete_slots', 'restore_slots']
    
    class Media:
        css = {
            'all': ('css/clear_errors.css',)
        }
        js = (
            'js/restrict_past_dates.js',
            'js/clear_field_errors.js',
        )


    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def sr_no(self, obj):
        """Display serialized Sr No instead of database ID"""
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        start_index = (page_num - 1) * self.list_per_page + 1
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index
    sr_no.short_description = "Sr No"


    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def sr_no(self, obj):
        """Display serialized Sr No instead of database ID"""
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        start_index = (page_num - 1) * self.list_per_page + 1
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index
    sr_no.short_description = "Sr No"


    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def sr_no(self, obj):
        """Display serialized Sr No instead of database ID"""
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        start_index = (page_num - 1) * self.list_per_page + 1
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index
    sr_no.short_description = "Sr No"

    # -------------------------
    # Display serial number
    # -------------------------
    def sr_no(self, obj):
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        start_index = (page_num - 1) * self.list_per_page + 1
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index
    sr_no.short_description = "Sr No"

    # -------------------------
    # Display booked capacity
    # -------------------------
    def booked_capacity_display(self, obj):
        return obj.booked_capacity()
    booked_capacity_display.short_description = "Booked"

    # -------------------------
    # Display remaining capacity
    # -------------------------
    def remaining_capacity_display(self, obj):
        return obj.remaining_capacity()
    remaining_capacity_display.short_description = "Available"


    # -------------------------
    # Include deleted slots in queryset
    # -------------------------
    def get_queryset(self, request):
        self.request = request  # Needed for sr_no calculation
        return super().get_queryset(request)


    def save_model(self, request, obj, form, change):
        """Validate that start_time and end_time are not in the past"""
        now = timezone.now()
        
        if obj.start_time < now:
            self.message_user(request, "Error: Start time cannot be in the past.", level='error')
            return
        
        if obj.end_time < now:
            self.message_user(request, "Error: End time cannot be in the past.", level='error')
            return
        
        if obj.end_time <= obj.start_time:
            self.message_user(request, "Error: End time must be after start time.", level='error')
            return
        
        super().save_model(request, obj, form, change)

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
