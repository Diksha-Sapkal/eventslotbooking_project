from types import MethodType
from django.contrib import admin

# Define the desired order for Django admin apps/models
APP_MENU_ORDER = {
    "Bookings": 6,
    "Events": 4,
    "Slots": 5,
    "Users": 2,
    "Venues": 3,
    "Authentication and Authorization": 1,
}


def _menu_sort_key(name: str) -> tuple:
    rank = APP_MENU_ORDER.get(name, len(APP_MENU_ORDER) + 1)
    return (rank, name)


def _ranked_app_list(self, request):
    app_list = self._original_get_app_list(request)
    for app in app_list:
        app['models'].sort(key=lambda m: _menu_sort_key(m['name']))
    app_list.sort(key=lambda app: _menu_sort_key(app['name']))
    return app_list


# Preserve the original method and apply ranking
if not hasattr(admin.site, "_original_get_app_list"):
    admin.site._original_get_app_list = admin.site.get_app_list
    admin.site.get_app_list = MethodType(_ranked_app_list, admin.site)

