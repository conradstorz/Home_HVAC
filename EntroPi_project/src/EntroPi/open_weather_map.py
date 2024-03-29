"""Functions for retrieving weather conditions for area where this monitor is located."""

from loguru import logger
import os
import requests

@logger.catch
def get_local_conditions(ENV_VARS, zipcode=None):
    """Contact weather underground and return a tuple of temperature for given zipcode and humidity."""

    # api_key = os.environ.get('OPEN_WEATHER_API')
    # line above won't work when this script is run from a service
    api_key = ENV_VARS['OPEN_WEATHER_API']
    logger.debug(f'{api_key=}')

    # TODO set these values from a ZipCode lookup
    lat = '38.317139'
    lon = '-85.868167'

    temp = None
    humid = None   
    response = None 

    url = f"https://api.openweathermap.org/data/2.5/weather?units=imperial&lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as err:
        logger.error("Exception from request library.")    
        logger.error(err)     
    
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
    