"""
Serializers for bookings application.
"""
from rest_framework import serializers
from .models import Booking, Ticket, TicketStatus, BookingStatus
from apps.flights.serializers import FlightSerializer
from apps.users.serializers import PassengerSerializer


class TicketSerializer(serializers.ModelSerializer):
    """Full ticket representation with nested flight and passenger info."""
    flight = FlightSerializer(read_only=True)
    passenger = PassengerSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'booking', 'passenger', 'flight',
            'seat_number', 'booking_date',
            'price', 'status', 'status_display'
        ]
        read_only_fields = ['id', 'booking_date', 'price']


class BookingSerializer(serializers.ModelSerializer):
    """Full booking with nested tickets."""
    tickets = TicketSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_email', 'status', 'status_display',
            'total_price', 'created_at', 'updated_at',
            'notes', 'tickets'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']


class CreateBookingSerializer(serializers.Serializer):
    """
    UC-001: Input for booking a ticket.
    Validates flight availability and seat.
    """
    flight_id = serializers.IntegerField()
    seat_number = serializers.CharField(max_length=10)

    def validate_flight_id(self, value):
        from apps.flights.models import Flight
        try:
            flight = Flight.objects.get(pk=value)
        except Flight.DoesNotExist:
            raise serializers.ValidationError('Flight not found.')
        if not flight.is_bookable:
            raise serializers.ValidationError(
                f'Flight {flight.flight_number} is not available for booking '
                f'(status: {flight.get_status_display()}, seats: {flight.available_seats}).'
            )
        return value

    def validate(self, attrs):
        from apps.flights.models import Flight
        from .models import Ticket
        flight = Flight.objects.get(pk=attrs['flight_id'])
        seat = attrs['seat_number']

        # Check seat is not already booked
        if Ticket.objects.filter(
            flight=flight,
            seat_number=seat,
            status=TicketStatus.ACTIVE
        ).exists():
            raise serializers.ValidationError(
                {'seat_number': f'Seat {seat} on this flight is already taken.'}
            )
        return attrs


class CancelBookingSerializer(serializers.Serializer):
    """Input for cancelling a booking."""
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)