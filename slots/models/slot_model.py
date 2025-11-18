# from django.db import models
# from events.models.event_model import Event


# class Slot(models.Model):
#     event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     capacity = models.PositiveIntegerField()
#     is_blocked = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)

#     def approved_attendees(self):
#         from bookings.models.booking_model import Booking  # local import to avoid circular dependency
#         return self.booking_set.filter(
#             booking_status=Booking.Status.APPROVED,
#             deleted_at__isnull=True
#         ).aggregate(models.Sum('attendees_count'))['attendees_count__sum'] or 0

#     def remaining_capacity(self):
#         remaining = self.capacity - self.approved_attendees()
#         return max(remaining, 0)

#     def booked_capacity(self):
#         return self.capacity - self.remaining_capacity()

#     def __str__(self):
#         return f"{self.event.name} | {self.start_time.strftime('%b %d %Y, %I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Slot(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    is_blocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)
    def approved_attendees(self):
        from bookings.models.booking_model import Booking
        return self.booking_set.filter(
            booking_status=Booking.Status.APPROVED,
            deleted_at__isnull=True
        ).aggregate(models.Sum('attendees_count'))['attendees_count__sum'] or 0

    def remaining_capacity(self):
        remaining = self.capacity - self.approved_attendees()
        return max(remaining, 0)

    def booked_capacity(self):
        return self.capacity - self.remaining_capacity()
    def clean(self):
        # -------------------------
        # 1️⃣ Basic validations
        # -------------------------
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be greater than start time.")

        if self.start_time < timezone.now():
            raise ValidationError("Start time cannot be in the past.")

        # -----------------------------------------
        # ⛔ If event not saved => skip overlap check
        # -----------------------------------------
        if not self.event_id:
            return

        # -------------------------
        # 2️⃣ Slot must fall inside event dates
        # -------------------------
        event = self.event

        if self.start_time.date() < event.start_date:
            raise ValidationError("Slot start time must be within event date range.")

        if self.end_time.date() > event.end_date:
            raise ValidationError("Slot end time must be within event date range.")

        # -------------------------
        # 3️⃣ No overlapping slots
        # -------------------------
        qs = Slot.objects.filter(
            event=self.event,
            deleted_at__isnull=True
        ).exclude(id=self.id)

        if qs.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists():
            raise ValidationError("This slot overlaps with an existing slot.")

    def __str__(self):
        return f"{self.event.name} | {self.start_time} - {self.end_time}"