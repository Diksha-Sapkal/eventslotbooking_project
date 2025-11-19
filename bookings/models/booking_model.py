

from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from users.models import User
from events.models.event_model import Event
from slots.models import Slot


class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    attendees_count = models.PositiveIntegerField(default=1)

    booking_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.id} - {self.user} - {self.slot}"

    # -------------------------------------------------------------
    # VALIDATIONS
    # -------------------------------------------------------------
    def clean(self):
        # Skip ALL validation when cancelling
        if self.booking_status == Booking.Status.CANCELLED:
            return

        errors = {}
        general = []

        slot = self.slot
        event = self.event

        # Slot / Event mismatch
        if slot.event_id != event.id:
            general.append("Selected slot does not belong to this event.")

        # Slot blocked
        if slot.is_blocked:
            general.append("This slot is blocked and cannot be booked.")

        # Invalid attendee count
        if self.attendees_count <= 0:
            errors["attendees_count"] = "Attendees count must be greater than zero."

        # Current approved attendees
        total_approved = Booking.objects.filter(
            slot=slot,
            booking_status=Booking.Status.APPROVED,
            deleted_at__isnull=True,
        ).exclude(pk=self.pk).aggregate(sum=Sum("attendees_count"))["sum"] or 0

        # Seats requested by this booking
        total_requested = total_approved + self.attendees_count

        # Capacity validation
        if total_requested > slot.capacity:
            general.append("slot capacity exceeded.")

        if general:
            errors["__all__"] = general

        if errors:
            raise ValidationError(errors)

    # -------------------------------------------------------------
    # SAVE: auto block/unblock slot
    # -------------------------------------------------------------
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not is_new:
            old_status = Booking.objects.filter(pk=self.pk).values_list(
                "booking_status", flat=True
            ).first()
        else:
            old_status = None

        # Validate before saving
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)

            slot = self.slot
            remaining = slot.remaining_capacity()

            # Slot becomes full → auto block
            if remaining <= 0 and not slot.is_blocked:
                Slot.objects.filter(pk=slot.pk).update(is_blocked=True)

            # Slot has space → auto unblock
            elif remaining > 0 and slot.is_blocked:
                Slot.objects.filter(pk=slot.pk).update(is_blocked=False)

    # -------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------
    def cancel(self):
        if self.booking_status != Booking.Status.CANCELLED:
            self.booking_status = Booking.Status.CANCELLED
            self.save(update_fields=["booking_status", "updated_at"])

    def approve(self):
        if self.booking_status != Booking.Status.APPROVED:
            self.booking_status = Booking.Status.APPROVED
            self.save(update_fields=["booking_status", "updated_at"])
