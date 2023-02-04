"""Constant values used throughout various functions"""
from datetime import datetime, timedelta

ZIPCODE = "47119"
WELCOME_MESSAGE = "Hello\nCircuitPython"
EXIT_MESSAGE = "Going to sleep\nCya later!"
BASENAME_CSV_FILE = "_HVAC_temps"
SENSOR_JSON_FILE = "w1devices.json"
SENSOR_DEFINITIONS = "sensor_definitions.json"
TEMP_AND_HUMIDITY_FILE = "local_conditions.json"
DATE_FORMAT_AS_STRING = '%Y/%m/%d-%H:%M:%S'
TIME_NOW = datetime.now().strftime(DATE_FORMAT_AS_STRING)
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

