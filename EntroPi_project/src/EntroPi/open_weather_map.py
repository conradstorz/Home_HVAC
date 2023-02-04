"""Functions for retrieving weather conditions for area where this monitor is located."""

"""
TODO get outside temperature and humidity from open weather map and place into csv database with each reading of sensors.
TODO note that once per 12 minutes is probably frequent enough to check temps and humidity
Thank you for subscribing to Free OpenWeatherMap!

API key:
- Your API key is 5a51770d8fa87227c5c1a07f3f9240fd
- Within the next couple of hours, it will be activated and ready to use
- You can later create more API keys on your account page
- Please, always use your API key in each API call

Endpoint:
- Please, use the endpoint api.openweathermap.org for your API calls
- Example of API call:
api.openweathermap.org/data/2.5/weather?q=London,uk&APPID=5a51770d8fa87227c5c1a07f3f9240fd

lat = '38.317139'
lon = '-85.868167'
API = '5a51770d8fa87227c5c1a07f3f9240fd'
url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API}"

Useful links:
- API documentation https://openweathermap.org/api
- Details of your plan https://openweathermap.org/price
- Please, note that 16-days daily forecast and History API are not available for Free subscribers
"""
from loguru import logger


@logger.catch
def get_local_conditions(zipcode=None):
    """Contact weather underground and return a tuple of temperature for given zipcode and humidity."""
    temp = 0
    humid = 0
    return (temp, humid)
