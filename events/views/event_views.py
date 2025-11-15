from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from events.models.event_model import Event
from events.serializers.event_serializer import EventSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Swagger Example Body
event_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example='Annual Tech Conference'),
        'venue': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        'description': openapi.Schema(type=openapi.TYPE_STRING, example='A tech meetup for developers'),
        'start_date': openapi.Schema(type=openapi.TYPE_STRING, example='2025-11-20'),
        'end_date': openapi.Schema(type=openapi.TYPE_STRING, example='2025-11-22'),
    }
)


@swagger_auto_schema(method='get', responses={200: EventSerializer(many=True)})
@swagger_auto_schema(method='post', request_body=event_example, responses={201: EventSerializer()})
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def event_list(request):
    """
    GET => Public catalog of events
    POST => Authenticated creation
    """
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        events = Event.objects.filter(deleted_at__isnull=True).filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

        if start_date:
            events = events.filter(start_date__gte=start_date)
        if end_date:
            events = events.filter(end_date__lte=end_date)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 10))
        result_page = paginator.paginate_queryset(events.order_by('start_date'), request)
        serializer = EventSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            "message": "Events fetched successfully",
            "data": serializer.data
        })

    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save()
        return Response({
            "message": "Event created successfully",
            "data": EventSerializer(event).data
        }, status=status.HTTP_201_CREATED)
    return Response({"message": "Event creation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: EventSerializer()})
@swagger_auto_schema(method='patch', request_body=event_example)
@swagger_auto_schema(method='delete', responses={200: "Event deleted successfully"})
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, deleted_at__isnull=True)

    if request.method == 'GET':
        serializer = EventSerializer(event)
        return Response({"message": "Event fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Event updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Event update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    event.deleted_at = timezone.now()
    event.save(update_fields=['deleted_at'])
    return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)