from rest_framework import serializers
from django.utils import timezone
from events.models.event_model import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'venue', 'description', 'start_date', 'end_date',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['deleted_at', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        today = timezone.now().date()

        if start_date and start_date < today:
            raise serializers.ValidationError("Event start date cannot be in the past.")

        if end_date and end_date < today:
            raise serializers.ValidationError("Event end date cannot be in the past.")

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Event start date cannot be after end date.")
        return attrs
