from django.db import models
from events.models.event_model import Event


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
        from bookings.models.booking_model import Booking  # local import to avoid circular dependency
        return self.booking_set.filter(
            booking_status=Booking.Status.APPROVED,
            deleted_at__isnull=True
        ).aggregate(models.Sum('attendees_count'))['attendees_count__sum'] or 0

    def remaining_capacity(self):
        remaining = self.capacity - self.approved_attendees()
        return max(remaining, 0)

    def booked_capacity(self):
        return self.capacity - self.remaining_capacity()

    def __str__(self):
        return f"{self.event.name} | {self.start_time.strftime('%b %d %Y, %I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"