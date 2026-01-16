import requests
import json
from config import WEATHER_TOKEN
from datetime import datetime, timedelta


weather_cache = dict()


def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_TOKEN}&units=metric'
    return requests.get(url)


def get_weather_temp(city):
    if city in weather_cache:
        if datetime.now() - weather_cache[city][0] < timedelta(hours=1):
            return weather_cache[city][1]

    res = get_weather(city)
    if res.status_code != 200:
        return 0
    temp = json.loads(res.text)["main"]["temp"]
    weather_cache[city] = (datetime.now(), temp)
    return temp
