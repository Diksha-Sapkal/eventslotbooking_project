"""
URL configuration for eventslotbooking_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse
from eventslotbooking_project import admin_menu  # noqa: F401

schema_view = get_schema_view(
   openapi.Info(
      title="Event & Slot Booking API",
      default_version='v1',
      description="APIs for Event & Slot Booking Platform",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
  
)

urlpatterns = [
    # Admin route
    path("admin/", admin.site.urls),
    # swagger and redoc views
    path('accounts/', include('django.contrib.auth.urls')),

    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Root endpoint
    path("", lambda request: HttpResponse("Welcome to Event & Slot Booking API 🚀")),

    # Users Auth APIs
    path("api/auth/", include("users.urls.auth_urls")),  # ✅ include auth_urls.py
    # Venues App
    path("api/venues/", include("venues.urls.venue_urls")),
    # Events App
    path('api/events/', include('events.urls')),
    # Slots App
    path("api/slots/", include("slots.urls.slot_urls")),
    # Bookings App
    path("api/bookings/", include("bookings.urls.booking_urls")),

]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)