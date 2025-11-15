from django.urls import path
from venues.views.venue_views import (
    venue_list,
    venue_detail,
)

urlpatterns = [
    path('', venue_list, name='venue_list'),
    path('<int:pk>/', venue_detail, name='venue_detail'),
]
