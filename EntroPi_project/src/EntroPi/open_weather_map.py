"""Functions for retrieving weather conditions for area where this monitor is located."""

from loguru import logger
import os
import requests

@logger.catch
def get_local_conditions(zipcode=None):
    """Contact weather underground and return a tuple of temperature for given zipcode and humidity."""

    api_key = os.environ.get('OPEN_WEATHER_API')
    lat = '38.317139'
    lon = '-85.868167'

    url = f"https://api.openweathermap.org/data/2.5/weather?units=imperial&lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)

    temp = None
    humid = None
    
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humid = data['main']['humidity']
    else:
        print("Failed to retrieve data from API")    
        print(url)

    return (temp, humid)
