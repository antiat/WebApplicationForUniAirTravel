from django.contrib import admin
from .models import Booking, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ['booking_date', 'price']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username', 'user__email']
    inlines = [TicketInline]
    readonly_fields = ['created_at', 'updated_at', 'total_price']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'flight', 'seat_number', 'status', 'price']
    list_filter = ['status']
    search_fields = ['passenger__first_name', 'passenger__last_name', 'flight__flight_number']