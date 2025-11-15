from django.urls import path
from slots.views.slot_views import (
    slot_list,
    slot_detail,
)

urlpatterns = [
    path('', slot_list, name='slot_list'),
    path('<int:pk>/', slot_detail, name='slot_detail'),
]
