import datetime

from django.conf import settings

import requests

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(('GET',))
def weather_detail_view(request):
    url = 'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}'.format(
        lat=35.045631,
        lon=-85.309677,
        api_key=settings.OPEN_WEATHER_API_KEY,
    )
    response = requests.get(url)

    assert response.status_code == 200

    response_json = response.json()

    timezone_offset_seconds = response_json['city']['timezone']
    timezone = datetime.timezone(datetime.timedelta(seconds=timezone_offset_seconds))

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
        'forecasts': forecasts,
    })
