"""
Management command: seed_data
Populates the database with realistic test data for development.
Usage: python manage.py seed_data
"""
import random
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.models import User, Passenger
from apps.flights.models import Airport, Aircraft, Flight, FlightStatus
from apps.bookings.models import Booking, Ticket, BookingStatus, TicketStatus


class Command(BaseCommand):
    help = 'Seed database with test data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting data seed...'))
        self._create_airports()
        self._create_aircraft()
        self._create_flights()
        self._create_users()
        self.stdout.write(self.style.SUCCESS('✓ Seed complete!'))

    def _create_airports(self):
        airports_data = [
            {'name': 'Sheremetyevo International Airport', 'city': 'Moscow', 'country': 'Russia', 'code': 'SVO'},
            {'name': 'Domodedovo International Airport', 'city': 'Moscow', 'country': 'Russia', 'code': 'DME'},
            {'name': 'Pulkovo Airport', 'city': 'Saint Petersburg', 'country': 'Russia', 'code': 'LED'},
            {'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA', 'code': 'JFK'},
            {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK', 'code': 'LHR'},
            {'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France', 'code': 'CDG'},
            {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany', 'code': 'FRA'},
            {'name': 'Dubai International Airport', 'city': 'Dubai', 'country': 'UAE', 'code': 'DXB'},
            {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey', 'code': 'IST'},
            {'name': 'Boryspil International Airport', 'city': 'Kyiv', 'country': 'Ukraine', 'code': 'KBP'},
        ]
        for data in airports_data:
            Airport.objects.get_or_create(code=data['code'], defaults=data)
        self.stdout.write(f'  ✓ {len(airports_data)} airports')

    def _create_aircraft(self):
        aircraft_data = [
            {'model': 'Boeing 737-800', 'capacity': 162, 'airline': 'Aeroflot', 'registration_number': 'RA-73000'},
            {'model': 'Airbus A320neo', 'capacity': 180, 'airline': 'Aeroflot', 'registration_number': 'RA-73001'},
            {'model': 'Boeing 777-300ER', 'capacity': 402, 'airline': 'Aeroflot', 'registration_number': 'RA-73002'},
            {'model': 'Airbus A321', 'capacity': 220, 'airline': 'S7 Airlines', 'registration_number': 'RA-73003'},
            {'model': 'Boeing 737 MAX', 'capacity': 172, 'airline': 'Ural Airlines', 'registration_number': 'RA-73004'},
            {'model': 'Airbus A380-800', 'capacity': 555, 'airline': 'Emirates', 'registration_number': 'A6-EVA'},
        ]
        for data in aircraft_data:
            Aircraft.objects.get_or_create(
                registration_number=data['registration_number'],
                defaults=data
            )
        self.stdout.write(f'  ✓ {len(aircraft_data)} aircraft')

    def _create_flights(self):
        airports = list(Airport.objects.all())
        aircraft_list = list(Aircraft.objects.all())
        flight_count = 0
        now = timezone.now()

        routes = [
            ('SVO', 'LHR'), ('SVO', 'CDG'), ('SVO', 'FRA'), ('SVO', 'DXB'),
            ('DME', 'JFK'), ('DME', 'IST'), ('LED', 'SVO'), ('KBP', 'FRA'),
            ('LHR', 'JFK'), ('CDG', 'DXB'),
        ]

        airport_map = {a.code: a for a in airports}
        aircraft_cycle = aircraft_list * 5

        for i, (dep_code, arr_code) in enumerate(routes):
            if dep_code not in airport_map or arr_code not in airport_map:
                continue
            dep_airport = airport_map[dep_code]
            arr_airport = airport_map[arr_code]
            aircraft = aircraft_cycle[i]

            for day_offset in range(0, 14):
                dep_time = now + timedelta(days=day_offset, hours=random.randint(6, 20))
                duration = timedelta(hours=random.randint(2, 11), minutes=random.choice([0, 30]))
                arr_time = dep_time + duration

                flight_number = f'SU{1000 + i * 10 + day_offset}'
                price = Decimal(random.randint(80, 900))

                Flight.objects.get_or_create(
                    flight_number=flight_number,
                    defaults={
                        'departure_airport': dep_airport,
                        'arrival_airport': arr_airport,
                        'departure_time': dep_time,
                        'arrival_time': arr_time,
                        'aircraft': aircraft,
                        'status': FlightStatus.SCHEDULED,
                        'base_price': price,
                        'available_seats': aircraft.capacity,
                    }
                )
                flight_count += 1

        self.stdout.write(f'  ✓ {flight_count} flights')

    def _create_users(self):
        # Admin
        admin, created = User.objects.get_or_create(
            email='admin@airline.com',
            defaults={
                'username': 'admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Manager
        manager, created = User.objects.get_or_create(
            email='manager@airline.com',
            defaults={'username': 'manager', 'role': 'manager'}
        )
        if created:
            manager.set_password('manager123')
            manager.save()

        # Test passengers
        test_users = [
            ('ivan.petrov@example.com', 'ivan_petrov', 'Ivan', 'Petrov', 'RU1234567', 'Russian', '1990-05-15'),
            ('anna.smirnova@example.com', 'anna_smirnova', 'Anna', 'Smirnova', 'RU7654321', 'Russian', '1995-08-22'),
            ('john.doe@example.com', 'john_doe', 'John', 'Doe', 'US9876543', 'American', '1985-03-10'),
        ]
        for email, username, fn, ln, passport, nationality, bd in test_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': username, 'role': 'passenger'}
            )
            if created:
                user.set_password('password123')
                user.save()
                Passenger.objects.create(
                    user=user,
                    first_name=fn,
                    last_name=ln,
                    passport_number=passport,
                    nationality=nationality,
                    birth_date=bd,
                )

        self.stdout.write(f'  ✓ users (admin/manager/3 passengers)')
        self.stdout.write(self.style.WARNING('  Credentials: admin@airline.com / admin123'))
        self.stdout.write(self.style.WARNING('  Credentials: ivan.petrov@example.com / password123'))