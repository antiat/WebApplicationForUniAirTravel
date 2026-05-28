"""
Bookings application models.
Booking (session) and Ticket (per-flight-per-passenger).
"""
from django.db import models
from django.conf import settings


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CANCELLED = 'cancelled', 'Cancelled'


class TicketStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    USED = 'used', 'Used'
    CANCELLED = 'cancelled', 'Cancelled'


class Booking(models.Model):
    """
    Booking session — groups one or more tickets for a user.
    Created when user initiates the booking process (UC-001).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f'Booking #{self.id} — {self.user.username} [{self.status}]'

    def calculate_total(self):
        """Recalculate and save total from related tickets."""
        total = self.tickets.filter(
            status=TicketStatus.ACTIVE
        ).aggregate(
            total=models.Sum('price')
        )['total'] or 0
        self.total_price = total
        self.save(update_fields=['total_price'])


class Ticket(models.Model):
    """
    Individual ticket — links a passenger to a specific flight seat.
    Part of UC-001: Booking a ticket.
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    passenger = models.ForeignKey(
        'users.Passenger',
        on_delete=models.PROTECT,
        related_name='tickets'
    )
    flight = models.ForeignKey(
        'flights.Flight',
        on_delete=models.PROTECT,
        related_name='tickets'
    )
    seat_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.ACTIVE
    )

    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-booking_date']
        # Prevent double-booking a seat on the same flight
        unique_together = [['flight', 'seat_number']]

    def __str__(self):
        return (
            f'Ticket #{self.id} — '
            f'{self.passenger.full_name} | '
            f'{self.flight.flight_number} seat {self.seat_number}'
        )