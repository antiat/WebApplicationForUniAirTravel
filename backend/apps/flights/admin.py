from django.contrib import admin
from .models import Airport, Aircraft, Flight


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'city', 'country', 'is_active']
    search_fields = ['code', 'name', 'city', 'country']
    list_filter = ['country', 'is_active']


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'model', 'airline', 'capacity', 'is_active']
    search_fields = ['registration_number', 'model', 'airline']
    list_filter = ['airline', 'is_active']


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = [
        'flight_number', 'departure_airport', 'arrival_airport',
        'departure_time', 'status', 'available_seats', 'base_price'
    ]
    list_filter = ['status', 'departure_airport', 'arrival_airport']
    search_fields = ['flight_number']
    date_hierarchy = 'departure_time'
    raw_id_fields = ['departure_airport', 'arrival_airport', 'aircraft']