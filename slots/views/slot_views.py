from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from slots.models.slot_model import Slot
from slots.serializers.slot_serializer import SlotSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

# Swagger Example Body
slot_example = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'event': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        'start_time': openapi.Schema(type=openapi.TYPE_STRING, example='2025-11-20T10:00:00Z'),
        'end_time': openapi.Schema(type=openapi.TYPE_STRING, example='2025-11-20T11:00:00Z'),
        'capacity': openapi.Schema(type=openapi.TYPE_INTEGER, example=50),
        'is_blocked': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
    }
)


@swagger_auto_schema(method='get', responses={200: SlotSerializer(many=True)})
@swagger_auto_schema(method='post', request_body=slot_example)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def slot_list(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        event_id = request.GET.get('event')
        date_str = request.GET.get('date')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        is_blocked = request.GET.get('is_blocked')

        slots = Slot.objects.filter(deleted_at__isnull=True).filter(
            Q(event__name__icontains=search) |
            Q(event__venue__name__icontains=search)
        )
        if event_id:
            slots = slots.filter(event_id=event_id)

        def add_date_filter(queryset, key, value):
            parsed = parse_date(value)
            if parsed:
                if key == 'start':
                    return queryset.filter(start_time__date__gte=parsed)
                if key == 'end':
                    return queryset.filter(end_time__date__lte=parsed)
                if key == 'exact':
                    return queryset.filter(start_time__date=parsed)
            return queryset

        if date_str:
            slots = add_date_filter(slots, 'exact', date_str)
        if start_date:
            slots = add_date_filter(slots, 'start', start_date)
        if end_date:
            slots = add_date_filter(slots, 'end', end_date)

        if is_blocked is not None:
            if is_blocked.lower() in ['true', '1']:
                slots = slots.filter(is_blocked=True)
            elif is_blocked.lower() in ['false', '0']:
                slots = slots.filter(is_blocked=False)

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get('page_size', 10))
        result_page = paginator.paginate_queryset(slots.order_by('start_time'), request)
        serializer = SlotSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            "message": "Slots fetched successfully",
            "data": serializer.data
        })

    serializer = SlotSerializer(data=request.data)
    if serializer.is_valid():
        slot = serializer.save()
        return Response({
            "message": "Slot created successfully",
            "data": SlotSerializer(slot).data
        }, status=status.HTTP_201_CREATED)
    return Response({"message": "Slot creation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='get', responses={200: SlotSerializer()})
@swagger_auto_schema(method='patch', request_body=slot_example)
@swagger_auto_schema(method='delete', responses={200: "Slot deleted successfully"})
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def slot_detail(request, pk):
    slot = get_object_or_404(Slot, pk=pk, deleted_at__isnull=True)

    if request.method == 'GET':
        serializer = SlotSerializer(slot)
        return Response({"message": "Slot fetched successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'PATCH':
        serializer = SlotSerializer(slot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Slot updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Slot update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    slot.deleted_at = timezone.now()
    slot.save(update_fields=['deleted_at'])
    return Response({"message": "Slot deleted successfully"}, status=status.HTTP_200_OK)