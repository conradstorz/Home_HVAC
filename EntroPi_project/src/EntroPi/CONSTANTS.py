"""Constant values used throughout various functions"""
from datetime import datetime, timedelta
from loguru import logger
import json
from json.decoder import JSONDecodeError

DATE_FORMAT_AS_STRING = '%Y/%m/%d-%H:%M:%S'

@logger.catch
def time_now_string():
    """Returns the time and date when called formatted in a standard way."""
    return datetime.now().strftime(DATE_FORMAT_AS_STRING)

TIME_NOW = time_now_string()

ZIPCODE = "47119"
WELCOME_MESSAGE = "Hello\nCircuitPython"
EXIT_MESSAGE = "Going to sleep\nCya later!"
BASENAME_CSV_FILE = "_HVAC_temps"
CSV_FILE_BASE_DIR = "CSV/"
SENSOR_JSON_FILE = "w1devices.json"
SENSOR_DEFINITIONS = "sensor_definitions.json"
TEMP_AND_HUMIDITY_FILE = "local_conditions.json"
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



@logger.catch
def retrieve_json(file_name):
    """JSON file is a key/value file of device IDs of previously found devices."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, JSONDecodeError) as error:
        # TODO log this error: logger.info(f"Error with JSON file: {error}")
        data = {}
    return data



@logger.catch
def write_json(file_name, data_dict):
    """Accept a dictionary that describe sensors and
    write out to the specified JSON file."""
    # Save the updated JSON file
    with open(file_name, "w") as outfile:
        json.dump(data_dict, outfile, indent=2)
    return


if __name__ == '__main__':
    logger.info(time_now_string())
    