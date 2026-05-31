from django.urls import path
from .views import (
    BookingCreateView,
    UserBookingListView,
    BookingDetailView,
    BookingCancelView,
    UserTicketListView,
    AdminBookingListView,
)

urlpatterns = [
    # User
    path('', BookingCreateView.as_view(), name='booking_create'),
    path('my/', UserBookingListView.as_view(), name='my_bookings'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking_cancel'),
    path('tickets/', UserTicketListView.as_view(), name='my_tickets'),

    # Admin
    path('admin/all/', AdminBookingListView.as_view(), name='admin_bookings'),
]
