# from django.db import models
# from django.core.exceptions import ValidationError
# from users.models import User
# from events.models.event_model import Event
# from slots.models import Slot


# class Booking(models.Model):

#     class Status(models.TextChoices):
#         PENDING = "PENDING", "Pending"
#         APPROVED = "APPROVED", "Approved"
#         CANCELLED = "CANCELLED", "Cancelled"

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
#     attendees_count = models.PositiveIntegerField()

#     booking_status = models.CharField(
#         max_length=20,
#         choices=Status.choices,
#         default=Status.PENDING,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = 'booking'
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Booking #{self.id} - {self.user} - {self.slot}"

#     # ---------------- VALIDATION ----------------
#     def clean(self):
#         errors = {}
#         general_errors = []

#         # Check if slot_id and event_id are set (before accessing related objects)
#         if not self.slot_id or not self.event_id:
#             general_errors.append("Slot and Event are required.")
#             if general_errors:
#                 errors['__all__'] = general_errors
#             raise ValidationError(errors)

#         # Now safely access the related objects
#         slot = self.slot
#         event = self.event

#         # Slot belongs to event
#         if slot.event_id != event.id:
#             general_errors.append("Selected slot does not belong to the provided event.")

#         # Blocked slot
#         if slot.is_blocked:
#             general_errors.append("This slot is blocked and cannot be booked.")

#         # Deleted slot
#         if slot.deleted_at is not None:
#             general_errors.append("Cannot book a slot that is no longer active.")

#         # Attendees check
#         if self.attendees_count <= 0:
#             errors['attendees_count'] = "Attendees count must be greater than zero."

#         # Capacity validation (only applies for new bookings)
#         if not self.pk:
#             total_attendees = Booking.objects.filter(
#                 slot=slot,
#                 booking_status=Booking.Status.APPROVED,
#                 deleted_at__isnull=True
#             ).exclude(pk=self.pk).aggregate(
#                 models.Sum('attendees_count')
#             )['attendees_count__sum'] or 0

#             if self.attendees_count > slot.capacity:
#                 errors['attendees_count'] = "Attendees count exceeds slot capacity."

#             elif (self.booking_status == Booking.Status.APPROVED and
#                   total_attendees + self.attendees_count > slot.capacity):
#                 errors['slot'] = "Cannot approve booking: slot capacity exceeded."

#         # Overlap check (only new booking)
#         if self.user_id and slot:
#             overlapping = Booking.objects.filter(
#                 user=self.user,
#                 booking_status__in=[Booking.Status.PENDING, Booking.Status.APPROVED],
#                 deleted_at__isnull=True,
#                 slot__start_time__lt=slot.end_time,
#                 slot__end_time__gt=slot.start_time,
#             ).exclude(pk=self.pk)

#             if overlapping.exists():
#                 errors['slot'] = "You already have a booking that overlaps with this time."

#         if general_errors:
#             errors['__all__'] = general_errors

#         if errors:
#             raise ValidationError(errors)

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)

#     def cancel(self):
#         self.booking_status = Booking.Status.CANCELLED
#         self.save(update_fields=['booking_status', 'updated_at'])

#     def approve(self):
#         self.booking_status = Booking.Status.APPROVED
#         self.save(update_fields=['booking_status', 'updated_at'])

from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.models import F, Sum
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
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "booking"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.id} - {self.user} - {self.slot}"

    # -----------------------------------------------------
    # Validations
    # -----------------------------------------------------
    def clean(self):
        errors = {}
        general_errors = []

        # -----------------------------------------------
        # Required FK check (only on creation)
        # -----------------------------------------------
        if not self.pk:
            if not self.slot_id or not self.event_id:
                raise ValidationError({"__all__": "Slot and Event are required."})

        slot = self.slot
        event = self.event

        # Slot belongs to same event
        if slot.event_id != event.id:
            general_errors.append("Selected slot does not belong to this event.")

        # Slot blocked/deleted
        if getattr(slot, "is_blocked", False):
            general_errors.append("This slot is blocked and cannot be booked.")

        if slot.deleted_at is not None:
            general_errors.append("Cannot book a deleted or inactive slot.")

        # Attendee count
        if not self.attendees_count or self.attendees_count <= 0:
            errors["attendees_count"] = "Attendees count must be greater than zero."

        # -------------------------------------------------------------
        # Capacity validation
        # -------------------------------------------------------------
        total_approved = (
            Booking.objects.filter(
                slot=slot,
                booking_status=Booking.Status.APPROVED,
                deleted_at__isnull=True,
            )
            .exclude(pk=self.pk)
            .aggregate(sum=Sum("attendees_count"))["sum"]
            or 0
        )

        # If single booking exceeds slot capacity
        if self.attendees_count and self.attendees_count > slot.capacity:
            # If editing → field is read-only in admin → move to __all__
            if self.pk:
                general_errors.append("Attendees count exceeds slot capacity.")
            else:
                errors["attendees_count"] = "Attendees count exceeds slot capacity."

        # If approving booking would bust capacity
        if (
            self.booking_status == Booking.Status.APPROVED
            and total_approved + self.attendees_count > slot.capacity
        ):
            general_errors.append("Cannot approve booking: slot capacity exceeded.")

        # -------------------------------------------------------------
        # Overlap validation
        # -------------------------------------------------------------
        if self.user_id and self.slot_id:
            overlapping = Booking.objects.filter(
                user=self.user,
                booking_status__in=[
                    Booking.Status.PENDING,
                    Booking.Status.APPROVED,
                ],
                deleted_at__isnull=True,
                slot__start_time__lt=slot.end_time,
                slot__end_time__gt=slot.start_time,
            ).exclude(pk=self.pk)

            if overlapping.exists():
                general_errors.append(
                    "You already have a booking that overlaps with this time."
                )

        # Combine errors
        if general_errors:
            errors["__all__"] = general_errors

        if errors:
            raise ValidationError(errors)

    # -----------------------------------------------------
    # Save + slot capacity updates
    # -----------------------------------------------------
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        old_status = None
        if not is_new:
            try:
                old_status = (
                    Booking.objects.only("booking_status")
                    .get(pk=self.pk)
                    .booking_status
                )
            except Booking.DoesNotExist:
                old_status = None

        # Run validations
        self.full_clean()

        with transaction.atomic():
            super().save(*args, **kwargs)

            slot_id = self.slot.pk
            attendees = self.attendees_count

            # NEW approved booking
            if is_new and self.booking_status == Booking.Status.APPROVED:
                Slot.objects.filter(pk=slot_id).update(
                    capacity=F("capacity") - attendees
                )

            # approval from pending → approved
            elif (
                old_status == Booking.Status.PENDING
                and self.booking_status == Booking.Status.APPROVED
            ):
                Slot.objects.filter(pk=slot_id).update(
                    capacity=F("capacity") - attendees
                )

            # cancellation from approved → canceled
            elif (
                old_status == Booking.Status.APPROVED
                and self.booking_status == Booking.Status.CANCELLED
            ):
                Slot.objects.filter(pk=slot_id).update(
                    capacity=F("capacity") + attendees
                )

    # -----------------------------------------------------
    # Actions
    # -----------------------------------------------------
    def cancel(self):
        if self.booking_status != Booking.Status.CANCELLED:
            self.booking_status = Booking.Status.CANCELLED
            self.save(update_fields=["booking_status", "updated_at"])

    def approve(self):
        if self.booking_status != Booking.Status.APPROVED:
            self.booking_status = Booking.Status.APPROVED
            self.save(update_fields=["booking_status", "updated_at"])
