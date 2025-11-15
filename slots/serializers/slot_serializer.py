from rest_framework import serializers
from django.utils import timezone
from slots.models.slot_model import Slot


class SlotSerializer(serializers.ModelSerializer):
    remaining_capacity = serializers.SerializerMethodField(read_only=True)
    booked_capacity = serializers.SerializerMethodField(read_only=True)
    available_capacity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Slot
        fields = [
            'id', 'event', 'start_time', 'end_time',
            'capacity', 'booked_capacity', 'remaining_capacity', 'available_capacity',
            'is_blocked',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = [
            'deleted_at', 'created_at', 'updated_at',
            'remaining_capacity', 'booked_capacity', 'available_capacity'
        ]

    def get_remaining_capacity(self, obj):
        return obj.remaining_capacity()

    def get_booked_capacity(self, obj):
        return obj.booked_capacity()

    def get_available_capacity(self, obj):
        # alias for remaining capacity to satisfy API requirement
        return obj.remaining_capacity()

    def validate(self, attrs):
        start_time = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end_time = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        event = attrs.get('event', getattr(self.instance, 'event', None))
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', None))

        now = timezone.now()

        if start_time and start_time < now:
            raise serializers.ValidationError("Slot start time cannot be in the past.")

        if end_time and end_time <= start_time:
            raise serializers.ValidationError("Slot end time must be after the start time.")

        if event:
            if start_time and start_time.date() < event.start_date:
                raise serializers.ValidationError("Slot start time must fall within the event dates.")
            if end_time and end_time.date() > event.end_date:
                raise serializers.ValidationError("Slot end time must fall within the event dates.")

        if event and capacity and capacity > event.venue.capacity:
            raise serializers.ValidationError("Slot capacity cannot exceed the venue capacity.")

        # Prevent overlapping slots for the same event
        if event and start_time and end_time:
            overlapping = Slot.objects.filter(
                event=event,
                deleted_at__isnull=True,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError("Slot overlaps with an existing slot for this event.")

        return attrs
