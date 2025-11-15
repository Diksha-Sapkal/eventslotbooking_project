from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from bookings.models.booking_model import Booking
from bookings.serializers.booking_serializer import BookingSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Swagger example body for Booking
booking_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'event': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        'slot': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        'attendees_count': openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
        'booking_status': openapi.Schema(type=openapi.TYPE_STRING, example='PENDING'),
    }
)


@swagger_auto_schema(method='get', responses={200: BookingSerializer(many=True)})
@swagger_auto_schema(method='post', request_body=booking_example)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def booking_list(request):
    user = request.user
    if request.method == 'GET':
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status')
        event_id = request.GET.get('event')
        timeframe = request.GET.get('timeframe')  # upcoming / past

        bookings = Booking.objects.filter(deleted_at__isnull=True)
        if not user.is_staff and not user.is_superuser:
            bookings = bookings.filter(user=user)

        if search:
            bookings = bookings.filter(
                Q(event__name__icontains=search) |
                Q(slot__event__venue__name__icontains=search)
            )

        if status_filter:
            status_value = status_filter.upper()
            if status_value in Booking.Status.values:
                bookings = bookings.filter(booking_status=status_value)

        if event_id:
            bookings = bookings.filter(event_id=event_id)

        if timeframe:
            now = timezone.now()
            if timeframe.lower() == 'upcoming':
                bookings = bookings.filter(slot__start_time__gte=now)
            elif timeframe.lower() == 'past':
                bookings = bookings.filter(slot__end_time__lt=now)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 10))
        bookings = bookings.select_related('event', 'slot', 'user')
        result_page = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            "message": "Bookings fetched successfully",
            "data": serializer.data
        })

    serializer = BookingSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        booking = serializer.save()
        return Response({
            "message": "Booking created successfully",
            "data": BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)
    return Response({"message": "Booking creation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: BookingSerializer()})
@swagger_auto_schema(method='patch', request_body=booking_example)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, deleted_at__isnull=True)
    if not request.user.is_staff and booking.user != request.user:
        return Response({"message": "Not authorized to view this booking."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = BookingSerializer(booking)
        return Response({"message": "Booking fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    serializer = BookingSerializer(booking, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Booking updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Booking update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', responses={200: "Booking cancelled"})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, deleted_at__isnull=True)
    if not request.user.is_staff and booking.user != request.user:
        return Response({"message": "Not authorized to cancel this booking."}, status=status.HTTP_403_FORBIDDEN)

    if booking.booking_status == Booking.Status.CANCELLED:
        return Response({"message": "Booking is already cancelled."}, status=status.HTTP_200_OK)

    booking.cancel()
    return Response({"message": "Booking cancelled successfully"}, status=status.HTTP_200_OK)
