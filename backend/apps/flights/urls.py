"""
URL patterns for flights application.
"""
from django.urls import path
from .views import (
    FlightListView,
    FlightDetailView,
    AirportListView,
    AdminFlightListCreateView,
    AdminFlightDetailView,
    AdminAirportListCreateView,
    AdminAirportDetailView,
    AdminAircraftListCreateView,
    AdminAircraftDetailView,
)

urlpatterns = [
    # Public
    path('', FlightListView.as_view(), name='flight_list'),
    path('<int:pk>/', FlightDetailView.as_view(), name='flight_detail'),
    path('airports/', AirportListView.as_view(), name='airport_list'),

    # Admin — flights
    path('admin/', AdminFlightListCreateView.as_view(), name='admin_flight_list'),
    path('admin/<int:pk>/', AdminFlightDetailView.as_view(), name='admin_flight_detail'),

    # Admin — airports
    path('admin/airports/', AdminAirportListCreateView.as_view(), name='admin_airport_list'),
    path('admin/airports/<int:pk>/', AdminAirportDetailView.as_view(), name='admin_airport_detail'),

    # Admin — aircraft
    path('admin/aircraft/', AdminAircraftListCreateView.as_view(), name='admin_aircraft_list'),
    path('admin/aircraft/<int:pk>/', AdminAircraftDetailView.as_view(), name='admin_aircraft_detail'),
]
