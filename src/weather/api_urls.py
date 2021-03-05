from django.urls import path

from . import api_views

urlpatterns = (
    path('', api_views.weather_detail_view),
    path('location/', api_views.location_list_view),
    path('location/<uuid:identifier>/', api_views.location_detail_view),
)
