# venues/views/venue_views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from venues.models import Venue
from venues.serializers.venue_serializer import VenueSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Swagger Example Body
venue_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Royal Banquet Hall'),
        'address': openapi.Schema(type=openapi.TYPE_STRING, example='123 MG Road, Pune'),
        'city': openapi.Schema(type=openapi.TYPE_STRING, example='Pune'),
        'state': openapi.Schema(type=openapi.TYPE_STRING, example='Maharashtra'),
        'pincode': openapi.Schema(type=openapi.TYPE_STRING, example='411001'),
        'capacity': openapi.Schema(type=openapi.TYPE_INTEGER, example=250)
    }
)


@swagger_auto_schema(method='get', responses={200: VenueSerializer(many=True)})
@swagger_auto_schema(method='post', request_body=venue_example)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def venue_list(request):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        city = request.GET.get('city')
        venues = Venue.objects.filter(deleted_at__isnull=True).filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(pincode__icontains=search_query)
        )
        if city:
            venues = venues.filter(city__iexact=city)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 10))
        result_page = paginator.paginate_queryset(venues.order_by('name'), request)
        serializer = VenueSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            "message": "Venues fetched successfully",
            "data": serializer.data
        })

    serializer = VenueSerializer(data=request.data)
    if serializer.is_valid():
        venue = serializer.save()
        return Response({
            "message": "Venue created successfully",
            "data": VenueSerializer(venue).data
        }, status=status.HTTP_201_CREATED)
    return Response({"message": "Venue creation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: VenueSerializer()})
@swagger_auto_schema(method='patch', request_body=venue_example)
@swagger_auto_schema(method='delete', responses={200: "Venue deleted successfully"})
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def venue_detail(request, pk):
    venue = get_object_or_404(Venue, pk=pk, deleted_at__isnull=True)

    if request.method == 'GET':
        serializer = VenueSerializer(venue)
        return Response({"message": "Venue fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = VenueSerializer(venue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Venue updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Venue update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    venue.deleted_at = timezone.now()
    venue.save(update_fields=['deleted_at'])
    return Response({"message": "Venue deleted successfully"}, status=status.HTTP_200_OK)
