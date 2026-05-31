"""
Views for flights application.
Public flight search, admin CRUD for flights/airports/aircraft.
"""
from django.db.models import Q
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Airport, Aircraft, Flight
from .serializers import (
    AirportSerializer,
    AircraftSerializer,
    FlightSerializer,
    FlightWriteSerializer,
)
from apps.users.permissions import IsAdminUser, IsAdminOrManager


# ──────────────────────────────────────────
# Public endpoints (no auth required)
# ──────────────────────────────────────────

class FlightListView(generics.ListAPIView):
    """
    UC-001 support: List and search available flights.
    Public access — no authentication required.
    """
    serializer_class = FlightSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['departure_time', 'base_price', 'flight_number']
    ordering = ['departure_time']

    @extend_schema(
        summary='Search and list flights',
        tags=['Flights'],
        parameters=[
            OpenApiParameter('from_code', OpenApiTypes.STR, description='Departure airport IATA code'),
            OpenApiParameter('to_code', OpenApiTypes.STR, description='Arrival airport IATA code'),
            OpenApiParameter('from_city', OpenApiTypes.STR, description='Departure city'),
            OpenApiParameter('to_city', OpenApiTypes.STR, description='Arrival city'),
            OpenApiParameter('date', OpenApiTypes.DATE, description='Departure date (YYYY-MM-DD)'),
            OpenApiParameter('min_price', OpenApiTypes.FLOAT),
            OpenApiParameter('max_price', OpenApiTypes.FLOAT),
            OpenApiParameter('status', OpenApiTypes.STR),
        ]
    )
    def get_queryset(self):
        qs = Flight.objects.select_related(
            'departure_airport', 'arrival_airport', 'aircraft'
        )
        params = self.request.query_params

        # Filter by airport code
        from_code = params.get('from_code')
        to_code = params.get('to_code')
        if from_code:
            qs = qs.filter(departure_airport__code__iexact=from_code)
        if to_code:
            qs = qs.filter(arrival_airport__code__iexact=to_code)

        # Filter by city name
        from_city = params.get('from_city')
        to_city = params.get('to_city')
        if from_city:
            qs = qs.filter(departure_airport__city__icontains=from_city)
        if to_city:
            qs = qs.filter(arrival_airport__city__icontains=to_city)

        # Filter by date
        date = params.get('date')
        if date:
            qs = qs.filter(departure_time__date=date)

        # Price range
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        if min_price:
            qs = qs.filter(base_price__gte=min_price)
        if max_price:
            qs = qs.filter(base_price__lte=max_price)

        # Status filter
        flight_status = params.get('status')
        if flight_status:
            qs = qs.filter(status=flight_status)
        else:
            # By default, show only scheduled and available
            qs = qs.filter(status__in=['scheduled', 'boarding'])

        return qs


class FlightDetailView(generics.RetrieveAPIView):
    """Get single flight details by ID."""
    queryset = Flight.objects.select_related(
        'departure_airport', 'arrival_airport', 'aircraft'
    )
    serializer_class = FlightSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary='Get flight by ID', tags=['Flights'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AirportListView(generics.ListAPIView):
    """List all active airports — used for search dropdowns."""
    queryset = Airport.objects.filter(is_active=True)
    serializer_class = AirportSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'country', 'code']

    @extend_schema(summary='List airports', tags=['Airports'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ──────────────────────────────────────────
# Admin endpoints
# ──────────────────────────────────────────

class AdminFlightListCreateView(generics.ListCreateAPIView):
    """
    UC-003: Admin creates a new flight.
    Also lists all flights (including cancelled).
    """
    queryset = Flight.objects.select_related(
        'departure_airport', 'arrival_airport', 'aircraft'
    )
    permission_classes = [IsAdminOrManager]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FlightWriteSerializer
        return FlightSerializer

    @extend_schema(summary='[Admin] List all flights', tags=['Admin — Flights'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Create flight', tags=['Admin — Flights'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AdminFlightDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: retrieve, update, or delete a flight."""
    queryset = Flight.objects.select_related(
        'departure_airport', 'arrival_airport', 'aircraft'
    )
    permission_classes = [IsAdminOrManager]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FlightWriteSerializer
        return FlightSerializer

    @extend_schema(summary='[Admin] Get flight', tags=['Admin — Flights'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Update flight', tags=['Admin — Flights'])
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Delete flight', tags=['Admin — Flights'])
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AdminAirportListCreateView(generics.ListCreateAPIView):
    """Admin: manage airports."""
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrManager]

    @extend_schema(summary='[Admin] List airports', tags=['Admin — Airports'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Create airport', tags=['Admin — Airports'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AdminAirportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrManager]


class AdminAircraftListCreateView(generics.ListCreateAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [IsAdminOrManager]

    @extend_schema(summary='[Admin] List aircraft', tags=['Admin — Aircraft'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary='[Admin] Create aircraft', tags=['Admin — Aircraft'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AdminAircraftDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer
    permission_classes = [IsAdminOrManager]
