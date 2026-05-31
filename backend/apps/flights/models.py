"""
Flights application models.
Airport, Aircraft, Flight entities.
"""
from django.db import models


class Airport(models.Model):
    """Airport entity — departure/arrival point for flights."""
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # IATA code e.g. SVO, JFK
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'airports'
        verbose_name = 'Airport'
        verbose_name_plural = 'Airports'
        ordering = ['country', 'city']

    def __str__(self):
        return f'{self.code} — {self.name} ({self.city}, {self.country})'


class Aircraft(models.Model):
    """Aircraft entity — plane used for flights."""
    model = models.CharField(max_length=100)   # e.g. Boeing 737, Airbus A320
    capacity = models.PositiveIntegerField()    # total seat count
    airline = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    manufactured_year = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'aircraft'
        verbose_name = 'Aircraft'
        verbose_name_plural = 'Aircraft'
        ordering = ['airline', 'model']

    def __str__(self):
        return f'{self.registration_number} — {self.model} ({self.airline})'


class FlightStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    BOARDING = 'boarding', 'Boarding'
    DEPARTED = 'departed', 'Departed'
    ARRIVED = 'arrived', 'Arrived'
    DELAYED = 'delayed', 'Delayed'
    CANCELLED = 'cancelled', 'Cancelled'


class Flight(models.Model):
    """
    Flight entity — the core of the airline system.
    Links airports, aircraft, times, and availability.
    """
    flight_number = models.CharField(max_length=20, unique=True)
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='departing_flights'
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='arriving_flights'
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.PROTECT,
        related_name='flights'
    )
    status = models.CharField(
        max_length=20,
        choices=FlightStatus.choices,
        default=FlightStatus.SCHEDULED
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flights'
        verbose_name = 'Flight'
        verbose_name_plural = 'Flights'
        ordering = ['departure_time']
        indexes = [
            models.Index(fields=['departure_time']),
            models.Index(fields=['flight_number']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return (
            f'{self.flight_number}: '
            f'{self.departure_airport.code} → {self.arrival_airport.code} '
            f'({self.departure_time.strftime("%Y-%m-%d %H:%M")})'
        )

    @property
    def duration_minutes(self):
        """Calculate flight duration in minutes."""
        delta = self.arrival_time - self.departure_time
        return int(delta.total_seconds() / 60)

    @property
    def is_bookable(self):
        """True if flight can be booked right now."""
        return (
            self.status == FlightStatus.SCHEDULED
            and self.available_seats > 0
        )

    def decrement_seats(self):
        """Atomically reduce available seats by 1."""
        if self.available_seats > 0:
            Flight.objects.filter(pk=self.pk).update(
                available_seats=models.F('available_seats') - 1
            )
            self.refresh_from_db()
        else:
            raise ValueError('No available seats on this flight.')

    def increment_seats(self):
        """Restore a seat on cancellation."""
        Flight.objects.filter(pk=self.pk).update(
            available_seats=models.F('available_seats') + 1
        )
        self.refresh_from_db()
