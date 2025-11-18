from django import forms
from django.contrib import admin
from django.utils import timezone
from events.models.event_model import Event
from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


class SlotInlineForm(forms.ModelForm):
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
        fields = ['start_time', 'end_time', 'capacity', 'is_blocked']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *"

    def clean(self):
        # ...existing code...
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and start_time < timezone.now():
            raise forms.ValidationError("Start time cannot be in the past.")
        
        if end_time and end_time < timezone.now():
            raise forms.ValidationError("End time cannot be in the past.")
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        return cleaned_data


class SlotInline(admin.TabularInline):
    # ...existing code...
    model = Slot
    form = SlotInlineForm
    extra = 1
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    fields = ['start_time', 'end_time', 'capacity', 'is_blocked', 'created_at', 'updated_at']
    can_delete = True


class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = ['name', 'venue', 'description', 'start_date', 'end_date']

<<<<<<< Updated upstream
<<<<<<< Updated upstream
def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      for field_name, field in self.fields.items():
        if field.required:
            label = field.label or field_name.replace('_', ' ').title()
            field.label = f"{label} *"
def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get('start_date')
    end_date = cleaned_data.get('end_date')
    today = timezone.now().date()  # compare dates only


    if start_date and start_date < today:
        raise forms.ValidationError("Event start date cannot be in the past.")

    if end_date and end_date < today:
        raise forms.ValidationError("Event end date cannot be in the past.")

    if start_date and end_date and start_date > end_date:
        raise forms.ValidationError("End date cannot be before start date.")

    return cleaned_data

=======
=======
>>>>>>> Stashed changes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *"

    def clean(self):
        # ...existing code...
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and start_date < timezone.now():
            raise forms.ValidationError("Event start date cannot be in the past.")
        
        if end_date and end_date < timezone.now():
            raise forms.ValidationError("Event end date cannot be in the past.")
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("End date must be after start date.")

        return cleaned_data


<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # ...existing code...
    form = EventForm
    list_display = ['sr_no', 'name', 'venue', 'description', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'venue__name']
    list_filter = ['venue', 'start_date', 'end_date']
    ordering = ['-created_at']
    list_per_page = 10
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = ['soft_delete_events', 'restore_events']
    inlines = [SlotInline]
    
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
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        start_index = (page_num - 1) * self.list_per_page + 1
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index
    sr_no.short_description = "Sr. No"
    # ...existing code...
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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not check_role_permission(request.user, 'Events', 'delete'):
            actions.pop('soft_delete_events', None)
        if not check_role_permission(request.user, 'Events', 'update'):
            actions.pop('restore_events', None)
        return actions

    def soft_delete_events(self, request, queryset):
        updated = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{updated} event(s) soft deleted.")
    soft_delete_events.short_description = "Soft delete selected events"

    def restore_events(self, request, queryset):
        updated = queryset.update(deleted_at=None)
        self.message_user(request, f"{updated} event(s) restored.")
    restore_events.short_description = "Restore selected events"