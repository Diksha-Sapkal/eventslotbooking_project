from django.urls import path
from bookings.views.booking_views import (
    booking_list,
    booking_detail,
    cancel_booking
)

urlpatterns = [
    path('', booking_list, name='booking_list'),
    path('<int:pk>/', booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
]
