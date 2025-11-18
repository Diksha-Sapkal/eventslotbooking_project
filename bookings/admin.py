# from django import forms
# from django.contrib import admin
# from django.http import HttpResponse
# from django.utils import timezone
# from django.core.exceptions import ValidationError
# import csv

# from bookings.models.booking_model import Booking
# from middleware.admin_administration_helpers import check_role_permission


# # ==========================
# #  Booking Change Form
# # ==========================
# class BookingStatusChangeForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['booking_status', 'attendees_count', 'user', 'event', 'slot']


# # ==========================
# #       Booking Admin
# # ==========================
# @admin.register(Booking)
# class BookingAdmin(admin.ModelAdmin):

#     list_display = [
#         'id',
#         'user',
#         'event',
#         'slot',
#         'slot_start',
#         'booking_status',
#         'attendees_count'
#     ]

#     # ❌ DO NOT USE list_editable (it breaks because required fields are hidden)
#     # list_editable = ['booking_status']

#     search_fields = [
#         'id',
#         'user__username',
#         'user__email',
#         'event__name',
#         'slot__start_time',
#         'slot__end_time',
#         'booking_status'
#     ]

#     list_filter = [
#         'booking_status',
#         'event',
#         'slot',
#         'user',
#         ('slot__start_time', admin.DateFieldListFilter),
#         'created_at',
#         'updated_at'
#     ]

#     ordering = ['-created_at']
#     list_per_page = 10

#     readonly_fields = ['created_at', 'updated_at', 'deleted_at']

#     exclude = ['user']

#     actions = [
#         'soft_delete_bookings',
#         'restore_bookings',
#         'approve_selected_bookings',
#         'cancel_selected_bookings',
#         'export_attendees_csv'
#     ]

#     # Slot Start Column
#     def slot_start(self, obj):
#         return obj.slot.start_time

#     slot_start.short_description = "Slot start"

#     # Readonly Control
#     def get_readonly_fields(self, request, obj=None):
#         base = ['created_at', 'updated_at', 'deleted_at']

#         is_super_admin = (
#             request.user.is_superuser or
#             (getattr(request.user, 'role', None) and request.user.role.name.lower() == 'superadmin')
#         )

#         if is_super_admin:
#             return base + ['user', 'event', 'slot', 'attendees_count']

#         return base

#     # Permissions
#     def has_module_permission(self, request):
#         return check_role_permission(request.user, 'Bookings', 'read')

#     def has_view_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Bookings', 'read')

#     def has_add_permission(self, request):
#         return check_role_permission(request.user, 'Bookings', 'create')

#     def has_change_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Bookings', 'update')

#     def has_delete_permission(self, request, obj=None):
#         return check_role_permission(request.user, 'Bookings', 'delete')

#     def get_model_perms(self, request):
#         module = 'Bookings'
#         return {
#             'add': check_role_permission(request.user, module, 'create'),
#             'change': check_role_permission(request.user, module, 'update'),
#             'delete': check_role_permission(request.user, module, 'delete'),
#             'view': check_role_permission(request.user, module, 'read'),
#         }

#     # Queryset
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)

#         is_super_admin = (
#             request.user.is_superuser or
#             (getattr(request.user, 'role', None) and request.user.role.name.lower() == 'superadmin')
#         )

#         if is_super_admin:
#             return qs

#         return qs.filter(user=request.user, deleted_at__isnull=True)

#     # Save Model
#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.user = request.user
#         try:
#             obj.save()
#         except ValidationError as e:
#             self.message_user(request, f"❌ {e}", level='error')

#     # ===== Custom Actions =====

#     # Soft delete
#     def soft_delete_bookings(self, request, queryset):
#         if not check_role_permission(request.user, 'Bookings', 'delete'):
#             self.message_user(request, "❌ You do not have permission to delete bookings.", level='error')
#             return

#         updated = queryset.update(deleted_at=timezone.now())
#         self.message_user(request, f"🗑️ {updated} booking(s) soft deleted.")

#     soft_delete_bookings.short_description = "🗑️ Soft delete selected bookings"

#     # Restore
#     def restore_bookings(self, request, queryset):
#         if not check_role_permission(request.user, 'Bookings', 'update'):
#             self.message_user(request, "❌ You do not have permission to update bookings.", level='error')
#             return

#         updated = queryset.update(deleted_at=None)
#         self.message_user(request, f"♻️ {updated} booking(s) restored.")

#     restore_bookings.short_description = "♻️ Restore selected bookings"

#     # Approve
#     def approve_selected_bookings(self, request, queryset):
#         if not check_role_permission(request.user, 'Bookings', 'update'):
#             self.message_user(request, "❌ You do not have permission to approve bookings.", level='error')
#             return

#         for booking in queryset:
#             try:
#                 booking.approve()
#             except ValidationError as e:
#                 self.message_user(request, f"❌ Booking {booking.id}: {e}", level='error')

#         self.message_user(request, "✅ Selected bookings approved.")

#     approve_selected_bookings.short_description = "✅ Approve selected bookings"

#     # Cancel
#     def cancel_selected_bookings(self, request, queryset):
#         if not check_role_permission(request.user, 'Bookings', 'update'):
#             self.message_user(request, "❌ You do not have permission to cancel bookings.", level='error')
#             return

#         for booking in queryset:
#             if booking.booking_status != Booking.Status.CANCELLED:
#                 booking.cancel()

#         self.message_user(request, "⚠️ Selected bookings cancelled.")

#     cancel_selected_bookings.short_description = "⚠️ Cancel selected bookings"

#     # CSV Export
#     def export_attendees_csv(self, request, queryset):
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename=\"bookings.csv\"'

#         writer = csv.writer(response)
#         writer.writerow(['Booking ID', 'User', 'Event', 'Slot Start', 'Status', 'Attendees'])

#         for booking in queryset.select_related('event', 'slot', 'user'):
#             writer.writerow([
#                 booking.id,
#                 booking.user.username,
#                 booking.event.name,
#                 booking.slot.start_time,
#                 booking.booking_status,
#                 booking.attendees_count
#             ])

#         return response

#     export_attendees_csv.short_description = "⬇️ Export attendees CSV"

# FILE: bookings/admin.py
# bookings/admin.py
from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.core.exceptions import ValidationError
import csv

from bookings.models.booking_model import Booking
from slots.models.slot_model import Slot
from middleware.admin_administration_helpers import check_role_permission


# -------------------------
# Booking change form (admin)
# -------------------------
class BookingStatusChangeForm(forms.ModelForm):
    class Media:
        js = ("bookings/admin_slot_filter.js",)

    required_css_class = "required"

    class Meta:
        model = Booking
        fields = ["booking_status", "attendees_count", "user", "event", "slot"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -----------------------------
        # CASE 1 - event selected in dropdown (POST)
        # -----------------------------
        if "event" in self.data:
            try:
                event_id = int(self.data.get("event"))
                self.fields["slot"].queryset = Slot.objects.filter(
                    event_id=event_id,
                    deleted_at__isnull=True
                )
                return
            except (ValueError, TypeError):
                pass

        # -----------------------------
        # CASE 2 - Edit existing booking 
        # -----------------------------
        if self.instance.pk:
            self.fields["slot"].queryset = Slot.objects.filter(
                event=self.instance.event,
                deleted_at__isnull=True
            )
            return

        # -----------------------------
        # CASE 3 - Add form first load (no event yet)
        # -----------------------------
        self.fields["slot"].queryset = Slot.objects.none()



@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingStatusChangeForm

    list_display = [
        "serial_number",
        "user",
        "event",
        "slot",
        "slot_start",
        "booking_status",
        "attendees_count",
    ]

    search_fields = [
        "id",
        "user__username",
        "user__email",
        "event__name",
        "slot__start_time",
        "slot__end_time",
        "booking_status",
    ]

    list_filter = [
        "booking_status",
        "event",
        "slot",
        "user",
        ("slot__start_time", admin.DateFieldListFilter),
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]
    list_per_page = 10

    readonly_fields = ["created_at", "updated_at", "deleted_at"]
    exclude = ["user"]

    # -------------------------
    # Most Important Fix:
    # Filter slot dropdown ALWAYS
    # -------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "slot":

            # CASE A — Edit form
            if request.resolver_match.kwargs.get("object_id"):
                booking_id = request.resolver_match.kwargs.get("object_id")
                try:
                    booking = Booking.objects.get(id=booking_id)
                    kwargs["queryset"] = Slot.objects.filter(
                        event=booking.event,
                        deleted_at__isnull=True,
                    )
                except Booking.DoesNotExist:
                    kwargs["queryset"] = Slot.objects.none()
                return super().formfield_for_foreignkey(db_field, request, **kwargs)

            # CASE B — Add form with ?event=<id>
            event_id = request.GET.get("event")
            if event_id:
                kwargs["queryset"] = Slot.objects.filter(
                    event_id=event_id,
                    deleted_at__isnull=True
                )
            else:
                kwargs["queryset"] = Slot.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    # -------------------------
    # Serial number
    # -------------------------
    def serial_number(self, obj):
        qs = Booking.objects.order_by("-created_at")
        index = list(qs).index(obj) + 1
        return index

    serial_number.short_description = "SR No"

    def slot_start(self, obj):
        return obj.slot.start_time

    slot_start.short_description = "Slot start"

    # -------------------------
    # Readonly fields per mode
    # -------------------------
    def get_readonly_fields(self, request, obj=None):
        base = ["created_at", "updated_at", "deleted_at"]
        if obj is None:
            return base
        return base + ["user", "event", "slot", "attendees_count"]

    # -------------------------
    # Permissions
    # -------------------------
    def has_module_permission(self, request):
        return check_role_permission(request.user, "Bookings", "read")

    def has_view_permission(self, request, obj=None):
        return check_role_permission(request.user, "Bookings", "read")

    def has_add_permission(self, request):
        return check_role_permission(request.user, "Bookings", "create")

    def has_change_permission(self, request, obj=None):
        return check_role_permission(request.user, "Bookings", "update")

    def has_delete_permission(self, request, obj=None):
        return check_role_permission(request.user, "Bookings", "delete")

    def get_model_perms(self, request):
        module = "Bookings"
        return {
            "add": check_role_permission(request.user, module, "create"),
            "change": check_role_permission(request.user, module, "update"),
            "delete": check_role_permission(request.user, module, "delete"),
            "view": check_role_permission(request.user, module, "read"),
        }

    # -------------------------
    # Queryset
    # -------------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deleted_at__isnull=True)

    # -------------------------
    # Save model
    # -------------------------
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

        try:
            obj.save()
        except ValidationError as e:
            self.message_user(request, f"❌ {e}", level="error")
