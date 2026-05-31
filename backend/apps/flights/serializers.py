"""
Serializers for flights application.
"""
from rest_framework import serializers
from .models import Airport, Aircraft, Flight, FlightStatus


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'name', 'city', 'country', 'code', 'timezone', 'is_active']


class AirportMinimalSerializer(serializers.ModelSerializer):
    """Compact airport info for nested use in flights."""
    class Meta:
        model = Airport
        fields = ['id', 'code', 'name', 'city', 'country']


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = [
            'id', 'model', 'capacity', 'airline',
            'registration_number', 'manufactured_year', 'is_active'
        ]


class FlightSerializer(serializers.ModelSerializer):
    """Full flight serializer with nested airport and aircraft info."""
    departure_airport = AirportMinimalSerializer(read_only=True)
    arrival_airport = AirportMinimalSerializer(read_only=True)
    aircraft = AircraftSerializer(read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time',
            'aircraft', 'status', 'status_display',
            'base_price', 'available_seats',
            'duration_minutes', 'is_bookable',
            'created_at', 'updated_at'
        ]


class FlightWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer — uses FK IDs for creation/update.
    Used by admin endpoints.
    """
    departure_airport = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.filter(is_active=True)
    )
    arrival_airport = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.filter(is_active=True)
    )
    aircraft = serializers.PrimaryKeyRelatedField(
        queryset=Aircraft.objects.filter(is_active=True)
    )

    class Meta:
        model = Flight
        fields = [
            'flight_number',
            'departure_airport', 'arrival_airport',
            'departure_time', 'arrival_time',
            'aircraft', 'status',
            'base_price', 'available_seats',
        ]

    def validate(self, attrs):
        dep = attrs.get('departure_airport') or self.instance and self.instance.departure_airport
        arr = attrs.get('arrival_airport') or self.instance and self.instance.arrival_airport
        dep_time = attrs.get('departure_time') or self.instance and self.instance.departure_time
        arr_time = attrs.get('arrival_time') or self.instance and self.instance.arrival_time

        if dep and arr and dep == arr:
            raise serializers.ValidationError(
                'Departure and arrival airports must be different.'
            )
        if dep_time and arr_time and arr_time <= dep_time:
            raise serializers.ValidationError(
                'Arrival time must be after departure time.'
            )
        return attrs

    def to_representation(self, instance):
        return FlightSerializer(instance, context=self.context).data


class FlightSearchSerializer(serializers.Serializer):
    """Query params serializer for flight search."""
    from_city = serializers.CharField(required=False, allow_blank=True)
    to_city = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField(required=False)
    min_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    status = serializers.ChoiceField(choices=FlightStatus.choices, required=False)
