"""
Service layer for bookings.
Encapsulates business logic, atomic operations.
"""
from django.db import transaction
from django.utils import timezone

from apps.flights.models import Flight
from apps.users.models import Passenger
from .models import Booking, Ticket, BookingStatus, TicketStatus


class BookingService:
    """
    Service class for the booking workflow (UC-001).
    All operations are atomic to maintain data integrity.
    """

    @staticmethod
    @transaction.atomic
    def create_booking(user, flight_id: int, seat_number: str) -> Booking:
        """
        Create a confirmed booking for a user on a given flight.

        Steps:
        1. Lock flight row for update.
        2. Validate seat availability.
        3. Create Booking + Ticket.
        4. Decrement available_seats.
        5. Return the booking.
        """
        # Get the passenger profile linked to this user
        try:
            passenger = user.passenger_profile
        except Passenger.DoesNotExist:
            raise ValueError('User does not have a passenger profile.')

        # Lock flight for atomic seat update
        flight = Flight.objects.select_for_update().get(pk=flight_id)

        if not flight.is_bookable:
            raise ValueError(
                f'Flight {flight.flight_number} cannot be booked '
                f'(status: {flight.get_status_display()}).'
            )

        # Check seat isn't taken (double-check after DB lock)
        if Ticket.objects.filter(
            flight=flight,
            seat_number=seat_number,
            status=TicketStatus.ACTIVE
        ).exists():
            raise ValueError(f'Seat {seat_number} is already taken.')

        # Create booking
        booking = Booking.objects.create(
            user=user,
            status=BookingStatus.CONFIRMED,
            total_price=flight.base_price,
        )

        # Create ticket
        Ticket.objects.create(
            booking=booking,
            passenger=passenger,
            flight=flight,
            seat_number=seat_number,
            price=flight.base_price,
            status=TicketStatus.ACTIVE,
        )

        # Decrement seats atomically
        flight.decrement_seats()

        return booking

    @staticmethod
    @transaction.atomic
    def cancel_booking(booking: Booking, user) -> Booking:
        """
        Cancel a booking and restore flight seat.

        Rules:
        - Only the owner or admin can cancel.
        - Cannot cancel already-cancelled bookings.
        - Restores available_seats for each active ticket.
        """
        if booking.status == BookingStatus.CANCELLED:
            raise ValueError('Booking is already cancelled.')

        # Check ownership
        if booking.user != user and not user.is_admin:
            raise PermissionError('You are not allowed to cancel this booking.')

        # Cancel all active tickets and restore seats
        active_tickets = booking.tickets.filter(status=TicketStatus.ACTIVE).select_related('flight')
        for ticket in active_tickets:
            ticket.status = TicketStatus.CANCELLED
            ticket.save(update_fields=['status'])
            ticket.flight.increment_seats()

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])

        return booking

    @staticmethod
    def get_user_bookings(user):
        """Return all bookings for a user with prefetched ticket/flight data."""
        return (
            Booking.objects
            .filter(user=user)
            .prefetch_related('tickets__flight__departure_airport', 'tickets__flight__arrival_airport')
            .order_by('-created_at')
        )
