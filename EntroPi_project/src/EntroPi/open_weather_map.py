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
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        logger.error("Exception from request library.")    
        logger.error(err)     
        temp = None
        humid = None
    
    if response == None:
        logger.error("Failed to get a response from request library.")    
        logger.error(url)        
        return (temp, humid)
    
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humid = data['main']['humidity']
    else:
        logger.error("Failed to retrieve data from API")    
        logger.error(url)

    return (temp, humid)


if __name__ == '__main__':
    logger.info(get_local_conditions())
    