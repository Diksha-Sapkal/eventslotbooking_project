# events/models/event_model.py
from django.db import models
from venues.models.venue_model import Venue
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete

    def __str__(self):
        return f"{self.name} - {self.venue.name}"

    class Meta:
        db_table = 'event'
