
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
        # CASE 1 — Event selected (POST)
        # -----------------------------
        if "event" in self.data:
            try:
                event_id = int(self.data.get("event"))
                if "slot" in self.fields:     # FIX
                    self.fields["slot"].queryset = Slot.objects.filter(
                        event_id=event_id,
                        deleted_at__isnull=True
                    )
                return
            except (ValueError, TypeError):
                pass

        # -----------------------------
        # CASE 2 — Editing an existing booking
        # -----------------------------
        if self.instance.pk:
            if "slot" in self.fields:         # FIX
                self.fields["slot"].queryset = Slot.objects.filter(
                    event=self.instance.event,
                    deleted_at__isnull=True
                )
            return

        # -----------------------------
        # CASE 3 — Add form (first load)
        # -----------------------------
        if "slot" in self.fields:             # FIX
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
    # Fix slot dropdown in Admin
    # -------------------------
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "slot":

            # CASE A — Editing an object
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

            # CASE B — Adding with ?event=<id>
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