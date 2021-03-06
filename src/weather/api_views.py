import datetime

from django.conf import settings

import requests

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core import cache

from . import models, serializers

class LocationViewSet(viewsets.ModelViewSet):
    lookup_field = 'identifier'
    serializer_class = serializers.LocationSerializer

    def get_queryset(self):
        return models.Location.objects.filter(user=self.request.user)

location_list_view = LocationViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

location_detail_view = LocationViewSet.as_view({
    'get': 'retrieve',
    'put': 'partial_update',
    'delete': 'destroy',
})

@cache.memoize(timeout=600)
def fetch_weather_data(latitude, longitude):
    url = 'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}'.format(
        lat=latitude,
        lon=longitude,
        api_key=settings.OPEN_WEATHER_API_KEY,
    )
    response = requests.get(url)

    assert response.status_code == 200

    return response.json()


@api_view(('GET',))
def weather_detail_view(request):
    latitude = request.GET['latitude']
    longitude = request.GET['longitude']

    response_json = fetch_weather_data(latitude, longitude)

    timezone_offset_seconds = response_json['city']['timezone']
    timezone = datetime.timezone(datetime.timedelta(seconds=timezone_offset_seconds))

    def strf_epoch_time(time, format_string):
        return datetime.datetime.fromtimestamp(
            time,
            tz=timezone,
        ).strftime(format_string)

    def format_location(city_data):
        utc_offset_hours = city_data['timezone'] / 60 / 60

        if utc_offset_hours == 0:
            utc_offset_display = 'UTC'
        else:
            utc_offset_display = 'UTC{0:+.2g}'.format(utc_offset_hours)

        sun_event_format = '%-I:%M%p'

        return {
            'name': city_data['name'],
            'latitude': city_data['coord']['lat'],
            'longitude': city_data['coord']['lon'],
            'timezone': utc_offset_display,
            'sunrise': strf_epoch_time(
                city_data['sunrise'],
                sun_event_format,
            ),
            'sunset': strf_epoch_time(
                city_data['sunset'],
                sun_event_format,
            ),
        }

    def format_forecast(forecast_data):
        timestamp = datetime.datetime.fromtimestamp(
            forecast_data['dt'],
            tz=timezone,
        )

        temperature = forecast_data['main']['temp']
        weather = [
            {
                'name': w['main'],
                'description': w['description'],
            } for w in forecast_data['weather']
        ]

        clouds_percent = forecast_data['clouds']['all']
        wind_speed = forecast_data['wind']['speed']
        probability_of_precipitation = forecast_data['pop']

        if forecast_data['sys']['pod'] == 'n':
            part_of_day = 'night'

        elif forecast_data['sys']['pod'] == 'd':
            part_of_day = 'day'

        return {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp_display': timestamp.strftime('%a %-I%p'),
            'temperature': temperature,
            'weather': weather,
            'clouds_percent': clouds_percent,
            'wind_speed': wind_speed,
            'probability_of_precipitation': probability_of_precipitation,
            'part_of_day': part_of_day,
        }

    forecasts = [format_forecast(f) for f in response_json['list'][:24]]

    return Response({
        'location': format_location(response_json['city']),
        'forecasts': forecasts,
    })
