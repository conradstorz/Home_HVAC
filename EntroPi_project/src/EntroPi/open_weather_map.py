"""Functions for retrieving weather conditions for area where this monitor is located."""

"""
TODO get outside temperature and humidity from open weather map and place into csv database with each reading of sensors.
TODO note that once per 12 minutes is probably frequent enough to check temps and humidity
Thank you for subscribing to Free OpenWeatherMap!

API key is now stored in the system environment

Endpoint:
- Please, use the endpoint api.openweathermap.org for your API calls
- Example of API call:
api.openweathermap.org/data/2.5/weather?q=London,uk&APPID=5a51770d8fa87227c5c1a07f3f9240fd

lat = '38.317139'
lon = '-85.868167'
API = see system environment variable
import os
api_key = os.environ.get('OPEN_WEATHER_API')
url = f"https://api.openweathermap.org/data/2.5/weather?units=imperial&lat={lat}&lon={lon}&appid={api_key}"

Useful links:
- API documentation https://openweathermap.org/api
- Details of your plan https://openweathermap.org/price
- Please, note that 16-days daily forecast and History API are not available for Free subscribers
"""
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
