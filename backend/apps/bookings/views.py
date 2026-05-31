"""
Views for bookings application.
UC-001: Book a ticket, view tickets, cancel booking.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Booking, Ticket
from .serializers import (
    BookingSerializer,
    CreateBookingSerializer,
    TicketSerializer,
    CancelBookingSerializer,
)
from .services import BookingService
from apps.users.permissions import IsAdminOrManager, IsOwnerOrAdmin


class BookingCreateView(APIView):
    """
    UC-001: Book a ticket on a flight.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Book a flight ticket',
        request=CreateBookingSerializer,
        responses={201: BookingSerializer},
        tags=['Bookings']
    )
    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = BookingService.create_booking(
                user=request.user,
                flight_id=serializer.validated_data['flight_id'],
                seat_number=serializer.validated_data['seat_number'],
            )
        except (ValueError, Exception) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class UserBookingListView(generics.ListAPIView):
    """List all bookings for the current user."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Get my bookings', tags=['Bookings'])
    def get_queryset(self):
        return BookingService.get_user_bookings(self.request.user)


class BookingDetailView(generics.RetrieveAPIView):
    """Get a single booking (owner or admin)."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Booking.objects.prefetch_related(
        'tickets__flight__departure_airport',
        'tickets__flight__arrival_airport',
        'tickets__passenger'
    )

    @extend_schema(summary='Get booking details', tags=['Bookings'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingCancelView(APIView):
    """Cancel a booking — restores seat availability."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Cancel a booking',
        request=CancelBookingSerializer,
        tags=['Bookings']
    )
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=404)

        try:
            cancelled = BookingService.cancel_booking(booking, request.user)
        except (ValueError, PermissionError) as e:
            return Response({'error': str(e)}, status=400)

        return Response(BookingSerializer(cancelled).data)


class UserTicketListView(generics.ListAPIView):
    """
    List all active tickets for the current user.
    Used for 'My Tickets' page.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Get my tickets', tags=['Tickets'])
    def get_queryset(self):
        return (
            Ticket.objects
            .filter(booking__user=self.request.user)
            .select_related(
                'flight__departure_airport',
                'flight__arrival_airport',
                'flight__aircraft',
                'passenger',
                'booking'
            )
            .order_by('-booking_date')
        )


# ──────────────────────────────────────────
# Admin endpoints
# ──────────────────────────────────────────

class AdminBookingListView(generics.ListAPIView):
    """Admin: view all bookings across all users."""
    queryset = Booking.objects.select_related('user').prefetch_related('tickets').order_by('-created_at')
    serializer_class = BookingSerializer
    permission_classes = [IsAdminOrManager]

    @extend_schema(summary='[Admin] List all bookings', tags=['Admin — Bookings'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
