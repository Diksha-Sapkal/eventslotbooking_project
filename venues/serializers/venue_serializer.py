from rest_framework import serializers
from venues.models import Venue

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'address', 'city', 'state', 'pincode',
            'capacity', 'created_at', 'updated_at', 'deleted_at'
        ]
