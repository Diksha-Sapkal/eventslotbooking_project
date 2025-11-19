# # events/admin.py

# from django import forms
# from django.contrib import admin
# from django.forms.models import BaseInlineFormSet
# from django.utils import timezone

# from events.models.event_model import Event
# from slots.models.slot_model import Slot
# from middleware.admin_administration_helpers import check_role_permission


# # -------------------------------------------------
# # SLOT FORM (no overlap logic here)
# # -------------------------------------------------
# class SlotInlineForm(forms.ModelForm):

#     start_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         input_formats=['%Y-%m-%dT%H:%M'],
#     )

#     end_time = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         input_formats=['%Y-%m-%dT%H:%M'],
#     )

#     class Meta:
#         model = Slot
#         fields = ['start_time', 'end_time', 'capacity', 'is_blocked']

#     def clean(self):
#         cleaned_data = super().clean()

#         start_time = cleaned_data.get("start_time")
#         end_time = cleaned_data.get("end_time")

#         if not start_time or not end_time:
#             return cleaned_data

#         if start_time >= end_time:
#             raise forms.ValidationError("End time must be after start time.")

#         if start_time < timezone.now():
#             raise forms.ValidationError("Start time cannot be in the past.")

#         return cleaned_data


# # -------------------------------------------------
# # INLINE FORMSET = responsible for unsaved overlap check
# # -------------------------------------------------
# class SlotFormSet(BaseInlineFormSet):

#     def clean(self):
#         super().clean()

#         # list of times to check overlap among unsaved forms
#         times = []

#         for form in self.forms:
#             if form.cleaned_data.get("DELETE"):
#                 continue

#             start = form.cleaned_data.get("start_time")
#             end = form.cleaned_data.get("end_time")

#             if not start or not end:
#                 continue

#             # Check overlap with other unsaved forms
#             for (other_start, other_end) in times:
#                 if start < other_end and end > other_start:
#                     raise forms.ValidationError(
#                         "Two slots in this form overlap. Please adjust times."
#                     )

#             times.append((start, end))


# # -------------------------------------------------
# # SLOT INLINE
# # -------------------------------------------------
# class SlotInline(admin.TabularInline):
#     model = Slot
#     form = SlotInlineForm
#     formset = SlotFormSet
#     extra = 1

#     readonly_fields = ['created_at', 'updated_at', 'deleted_at']
#     fields = ['start_time', 'end_time', 'capacity', 'is_blocked', 'created_at', 'updated_at']
#     can_delete = True


# # -------------------------------------------------
# # EVENT FORM
# # -------------------------------------------------
# class EventForm(forms.ModelForm):

#     start_date = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         input_formats=['%Y-%m-%d'],
#     )

#     end_date = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date'}),
#         input_formats=['%Y-%m-%d'],
#     )

#     class Meta:
#         model = Event
#         fields = ['name', 'venue', 'description', 'start_date', 'end_date']

#     def clean(self):
#         cleaned_data = super().clean()

#         start_date = cleaned_data.get("start_date")
#         end_date = cleaned_data.get("end_date")
#         today = timezone.now().date()

#         if start_date and start_date < today:
#             raise forms.ValidationError("Event start date cannot be in the past.")

#         if end_date and end_date < today:
#             raise forms.ValidationError("Event end date cannot be in the past.")

#         if start_date and end_date and end_date < start_date:
#             raise forms.ValidationError("End date cannot be before start date.")

#         return cleaned_data


# # -------------------------------------------------
# # EVENT ADMIN
# # -------------------------------------------------
# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#     form = EventForm
#     inlines = [SlotInline]

#     list_display = ['sr_no', 'name', 'venue', 'description', 'start_date', 'end_date']
#     search_fields = ['name', 'description', 'venue__name']
#     list_filter = ['venue', 'start_date', 'end_date']
#     ordering = ['-created_at']
#     list_per_page = 10

#     readonly_fields = ['created_at', 'updated_at', 'deleted_at']
#     actions = ['soft_delete_events', 'restore_events']

#     class Media:
#         css = {'all': ('css/clear_errors.css',)}
#         js = ('js/restrict_past_dates.js', 'js/clear_field_errors.js',)

#     def changelist_view(self, request, extra_context=None):
#         self.request = request
#         return super().changelist_view(request, extra_context)

#     def sr_no(self, obj):
#         queryset = self.get_queryset(self.request)
#         page_num = int(self.request.GET.get('p', 1))
#         current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
#         return (page_num - 1) * self.list_per_page + current_index

#     sr_no.short_description = "Sr. No"


# events/admin.py

from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils import timezone

from events.models.event_model import Event
from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


# -------------------------------------------------
# SLOT FORM
# -------------------------------------------------
class SlotInlineForm(forms.ModelForm):

    start_time = forms.DateTimeField(
        label="Start time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    end_time = forms.DateTimeField(
        label="End time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Slot
        fields = ['start_time', 'end_time', 'capacity', 'is_blocked']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add * to required fields
        for name, field in self.fields.items():
            if field.required and field.label:
                field.label = f"{field.label} *"

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # FIX: allow required validation to show
        if start_time is None or end_time is None:
            return cleaned_data

        if start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        if start_time < timezone.now():
            raise forms.ValidationError("Start time cannot be in the past.")

        return cleaned_data


# -------------------------------------------------
# INLINE FORMSET (overlap check)
# -------------------------------------------------
class SlotFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()
        times = []

        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue

            start = form.cleaned_data.get("start_time")
            end = form.cleaned_data.get("end_time")

            if not start or not end:
                continue

            for (other_start, other_end) in times:
                if start < other_end and end > other_start:
                    raise forms.ValidationError(
                        "Two slots in this form overlap. Please adjust times."
                    )

            times.append((start, end))


# -------------------------------------------------
# SLOT INLINE
# -------------------------------------------------
class SlotInline(admin.TabularInline):
    model = Slot
    form = SlotInlineForm
    formset = SlotFormSet
    extra = 1

    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    fields = ['start_time', 'end_time', 'capacity', 'is_blocked', 'created_at', 'updated_at']
    can_delete = True


# -------------------------------------------------
# EVENT FORM
# -------------------------------------------------
class EventForm(forms.ModelForm):

    start_date = forms.DateField(
        label="Start date",
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    end_date = forms.DateField(
        label="End date",
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = Event
        fields = ['name', 'venue', 'description', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add * to required fields
        for name, field in self.fields.items():
            if field.required and field.label:
                field.label = f"{field.label} *"

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        today = timezone.now().date()

        if start_date and start_date < today:
            raise forms.ValidationError("Event start date cannot be in the past.")

        if end_date and end_date < today:
            raise forms.ValidationError("Event end date cannot be in the past.")

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")

        return cleaned_data


# -------------------------------------------------
# EVENT ADMIN
# -------------------------------------------------
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm
    inlines = [SlotInline]

    list_display = ['sr_no', 'name', 'venue', 'description', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'venue__name']
    list_filter = ['venue', 'start_date', 'end_date']
    ordering = ['-created_at']
    list_per_page = 10

    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    actions = ['soft_delete_events', 'restore_events']

    class Media:
        css = {'all': ('css/clear_errors.css',)}
        js = ('js/restrict_past_dates.js', 'js/clear_field_errors.js',)

    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    def sr_no(self, obj):
        queryset = self.get_queryset(self.request)
        page_num = int(self.request.GET.get('p', 1))
        current_index = list(queryset.values_list('pk', flat=True)).index(obj.pk) + 1
        return (page_num - 1) * self.list_per_page + current_index

    sr_no.short_description = "Sr. No"