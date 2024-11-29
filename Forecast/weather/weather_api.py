import datetime
import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
import pandas as pd

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def weather_interpretation_codes(n):
    if n:
        n = str(int(n))
    codes_dict_ru = {
        "0": "Ясно",
        "1": "Преимущественно ясно",
        "2": "Переменная облачность",
        "3": "Пасмурно",
        "45": "Туман",
        "48": "Иней",
        "51": "Лёгкая морось",
        "53": "Умеренная морось",
        "55": "Густая морось",
        "56": "Лёгкая ледяная изморось",
        "57": "Густая ледяная изморось",
        "61": "Небольшой дождь",
        "63": "Умеренный дождь",
        "65": "Сильный дождь",
        "66": "Легкий ледяной дождь",
        "67": "Густой ледяной дождь",
        "71": "Слабый снегопад",
        "73": "Умеренный снегопад",
        "75": "Сильный снегопад",
        "77": "Снежные зерна",
        "80": "Слабые ливни",
        "81": "Умеренные ливни",
        "82": "Сильные ливни",
        "85": "Лёгкий снегопад  ",
        "86": "Сильный снегопад",
        "95": "Гроза",
        "96": "Гроза с небольшим градом",
        "99": "Гроза с сильным градом",
    }
    try:
        return codes_dict_ru[n]
    except KeyError:
        return 'Погодные условия не определены'


def wind_directions(n):
    if n:
        n = int(n)
    if n in range(337, 361) or n in range(0, 22):
        return 'с'
    elif n in range(23, 68):
        return 'св'
    elif n in range(68, 112):
        return 'в'
    elif n in range(112, 157):
        return 'юв'
    elif n in range(157, 202):
        return 'ю'
    elif n in range(202, 247):
        return 'юз'
    elif n in range(247, 292):
        return 'з'
    elif n in range(292, 337):
        return 'сз'


def pressure_converter(n):
    try:
        return n * 0.750064
    except TypeError:
        return -1


def get_weather_data(city):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    one_week = datetime.timedelta(days=7)
    two_weeks = datetime.timedelta(days=14)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "daily": ["temperature_2m_max",
                  "temperature_2m_min",
                  "precipitation_sum",
                  "wind_speed_10m_max",
                  "wind_direction_10m_dominant",
                  "weather_code",
                  "precipitation_probability_mean"],
        "current": ["temperature_2m",
                    "apparent_temperature",
                    "precipitation",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "weather_code",
                    "relative_humidity_2m",
                    "pressure_msl"],
        "timezone": "auto",
        "wind_speed_unit": "ms",
        "past_days": 0,
        "start_date": tomorrow + datetime.timedelta(days=1),
        "end_date": tomorrow + one_week,

    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    current = response.Current()

    current_time = {"date": pd.date_range(
        start=pd.to_datetime(current.Time(), unit="s"),
        end=pd.to_datetime(current.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=current.Interval()),
        inclusive="left"
    )}

    current_date = current_time["date"].strftime('%d.%m').tolist()

    current_weather_data = {
        "temperature": current.Variables(0).Value(),
        "apparent_temperature": current.Variables(1).Value(),
        "precipitation": current.Variables(2).Value(),
        "wind_speed": current.Variables(3).Value(),
        "wind_direction": wind_directions(current.Variables(4).Value()),
        "weather_code": weather_interpretation_codes(current.Variables(5).Value()),
        "relative_humidity": current.Variables(6).Value(),
        "pressure": pressure_converter(current.Variables(7).Value()),
        "current_date": current_date[0],
    }

    daily = response.Daily()
    date_range = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s"),
        end=pd.to_datetime(daily.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )}

    date_strings = date_range["date"].strftime('%d.%m').tolist()

    weather_data = [
        {
            "date": date_strings[i],
            "temperature_max": daily.Variables(0).ValuesAsNumpy()[i],
            "temperature_min": daily.Variables(1).ValuesAsNumpy()[i],
            "precipitation_sum": daily.Variables(2).ValuesAsNumpy()[i],
            "wind_speed_max": daily.Variables(3).ValuesAsNumpy()[i],
            "wind_direction": wind_directions(daily.Variables(4).ValuesAsNumpy()[i]),
            "weather_code": weather_interpretation_codes(daily.Variables(5).ValuesAsNumpy()[i]),
            "precipitation_probability_mean": daily.Variables(6).ValuesAsNumpy()[i],
        }
        for i in range(len(date_strings))
    ]

    context = {
        "current_weather_data": current_weather_data,
        "weather_data": weather_data,
        "latitude": response.Latitude(),
        "longitude": response.Longitude(),
        "elevation": response.Elevation(),
        "timezone": response.Timezone(),
        "timezone_abbreviation": response.TimezoneAbbreviation(),
        "utc_offset_seconds": response.UtcOffsetSeconds(),
    }
    return context


if __name__ == '__main__':
    get_weather_data('Chisinau')
