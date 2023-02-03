"""Constant values used throughout various functions"""
from datetime import datetime, timedelta

ZIPCODE = "47119"
WELCOME_MESSAGE = "Hello\nCircuitPython"
EXIT_MESSAGE = "Going to sleep\nCya later!"
BASENAME_CSV_FILE = "_HVAC_temps"
SENSOR_JSON_FILE = "w1devices.json"
SENSOR_DEFINITIONS = "sensor_definitions.json"
TIME_NOW = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
MIN_WEATHER_URL_UPDATE_INTERVAL = timedelta(minutes=12)
EXAMPLE_DICT = {
    "Device ID HEX value goes here": {
        "device location": None,
        "device type": None,
        "accuracy value": 9,
        "first seen date": TIME_NOW,
        "most recent date accessed": TIME_NOW,
        "temperature": None,
        "highest value": None,
        "highest date": TIME_NOW,
        "lowest value": None,
        "lowest date": TIME_NOW,
    }
}

"""     "last_weather_update": 0,
        "last_outside_temperature": None,
        "last_outdoor_humidity": None,
"""
