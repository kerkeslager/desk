from django.urls import path

from . import api_views

urlpatterns = (
    path('', api_views.weather_detail_view),
)
