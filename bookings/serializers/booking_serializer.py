from rest_framework import serializers
from bookings.models.booking_model import Booking


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)
    slot_start = serializers.DateTimeField(source='slot.start_time', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'event', 'event_name', 'slot', 'slot_start',
            'booking_status', 'attendees_count',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['deleted_at', 'created_at', 'updated_at', 'event_name', 'slot_start']

    def validate(self, attrs):
        event = attrs.get('event')
        slot = attrs.get('slot')

        if self.instance is None:
            request = self.context.get('request')
            user = request.user if request and request.user.is_authenticated else attrs.get('user')
            if not user:
                raise serializers.ValidationError("Authenticated user is required to create a booking.")
            attrs['user'] = user

        if slot and slot.deleted_at is not None:
            raise serializers.ValidationError({"slot": "Slot is not available."})

        if slot and event and slot.event_id != event.id:
            raise serializers.ValidationError({"slot": "Slot must belong to the same event."})

        if slot and not event:
            attrs['event'] = slot.event

        return attrs

    def create(self, validated_data):
        validated_data.setdefault('booking_status', Booking.Status.PENDING)
        return Booking.objects.create(**validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_staff or user.is_superuser:
                # Superadmins can only change status
                validated_data = {
                    key: value
                    for key, value in validated_data.items()
                    if key == 'booking_status'
                }
            else:
                # Non superadmins cannot tamper with status
                validated_data = {
                    key: value
                    for key, value in validated_data.items()
                    if key != 'booking_status'
                }
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
