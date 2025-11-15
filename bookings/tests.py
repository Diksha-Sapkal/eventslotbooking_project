from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User
from venues.models import Venue
from events.models.event_model import Event
from slots.models.slot_model import Slot
from bookings.models.booking_model import Booking
from datetime import timedelta


class BookingValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass1234', email='tester@example.com')
        self.venue = Venue.objects.create(
            name='Main Hall',
            address='123 Street',
            city='Pune',
            state='MH',
            pincode='411001',
            capacity=100
        )
        self.event = Event.objects.create(
            name='Tech Summit',
            venue=self.venue,
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )
        now = timezone.now()
        self.slot = Slot.objects.create(
            event=self.event,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            capacity=10
        )

    def test_blocked_slot_cannot_be_booked(self):
        self.slot.is_blocked = True
        self.slot.save()
        booking = Booking(
            user=self.user,
            event=self.event,
            slot=self.slot,
            attendees_count=2,
            booking_status=Booking.Status.PENDING
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_capacity_cannot_be_exceeded_when_approving(self):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            slot=self.slot,
            attendees_count=8,
            booking_status=Booking.Status.APPROVED
        )
        another_user = User.objects.create_user(username='second', password='pass1234', email='second@example.com')
        booking = Booking(
            user=another_user,
            event=self.event,
            slot=self.slot,
            attendees_count=5,
            booking_status=Booking.Status.APPROVED
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_overlapping_bookings_not_allowed_for_same_user(self):
        Booking.objects.create(
            user=self.user,
            event=self.event,
            slot=self.slot,
            attendees_count=2,
            booking_status=Booking.Status.APPROVED
        )
        overlapping_slot = Slot.objects.create(
            event=self.event,
            start_time=self.slot.start_time + timedelta(minutes=30),
            end_time=self.slot.end_time + timedelta(minutes=30),
            capacity=10
        )
        booking = Booking(
            user=self.user,
            event=self.event,
            slot=overlapping_slot,
            attendees_count=1,
            booking_status=Booking.Status.PENDING
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()
