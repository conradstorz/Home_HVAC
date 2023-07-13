""" TODO get outside temperature and humidity from open weather map and place into csv database with each reading of sensors.
TODO note that once per 12 minutes is probably frequent enough to check temps and humidity
Thank you for subscribing to Free OpenWeatherMap!

API key:
- Your API key is: DUH! it's a secret
- Within the next couple of hours, it will be activated and ready to use
- You can later create more API keys on your account page
- Please, always use your API key in each API call

Endpoint:
- Please, use the endpoint api.openweathermap.org for your API calls
- Example of API call:
api.openweathermap.org/data/2.5/weather?q=London,uk&APPID='a secret'

lat = '38.317139'
lon = '-85.868167'
API = 'DONT PUT IT HERE'
url = f"https://api.openweathermap.org/data/2.5/weather?units=imperial&lat={lat}&lon={lon}&appid={API}"

SAMPLE RETURN:

{"coord":{"lon":-85.8682,"lat":38.3171},
"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],
"base":"stations",
"main":{"temp":26.42,"feels_like":25.72,"temp_min":26.36,"temp_max":26.38,"pressure":1031,"humidity":61},
"visibility":10000,
"wind":{"speed":5.14,"deg":350,"gust":9.77},
"clouds":{"all":20},"dt":1675429404,
"sys":{"type":2,"id":2003995,"country":"US","sunrise":1675428420,"sunset":1675465650},
"timezone":-18000,
"id":4257565,
"name":"Floyd",
"cod":200}

import requests

url = "https://example.com/api/data"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # do something with data
else:
    logger.info("Failed to retrieve data from API")


Useful links:
- API documentation https://openweathermap.org/api
- Details of your plan https://openweathermap.org/price
- Please, note that 16-days daily forecast and History API are not available for Free subscribers
"""
from loguru import logger


@logger.catch
def get_temp_and_humidity(zipcode = None):
    """Retrieve current weather conditions in a JSON format and return a tuple of temp and humidity."""
    import requests

    lat = '38.317139'
    lon = '-85.868167'
    API = 'DONT PUT IT HERE IN UPLOADS TO GITHUB'
    url = f"https://api.openweathermap.org/data/2.5/weather?units=imperial&lat={lat}&lon={lon}&appid={API}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        logger.info(data)
    else:
        logger.info("Failed to retrieve data from API")

    """Contact weather underground and return a tuple of temperature for given zipcode and humidity."""
    temp = data['main']['temp']
    humid = data['main']['humidity']
    return (temp, humid)


if __name__ == '__main__':
    logger.info(get_temp_and_humidity())
