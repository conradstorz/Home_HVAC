"""Functions that directly access w1Therm type devices and return data."""

# load needed modules
import Adafruit_DHT
from w1thermsensor import W1ThermSensor, Sensor, Unit, errors
from loguru import logger
from datetime import datetime
from CONSTANTS import SENSOR_JSON_FILE
from CONSTANTS import retrieve_json
from CONSTANTS import EXAMPLE_DICT
from CONSTANTS import time_now_string


@logger.catch
def get_current_temps(sensor_dict):
    results = {}
    for deviceID, details in sensor_dict.items():
        results[deviceID] = details
        try:
            sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=f"{deviceID}")
            temperature_in_F = sensor.get_temperature(Unit.DEGREES_F)
            # limit temp reading to one decimal place
            temperature_in_F = round(temperature_in_F, 1)
        except (errors.SensorNotReadyError, errors.ResetValueError) as error:
            # TODO log error
            print(f'Error reading sensor: {deviceID} with error: {error}')
            temperature_in_F = None
        results[deviceID]["temperature"] = temperature_in_F
        results[deviceID]["most recent date accessed"] = time_now_string()
    return results


@logger.catch
def build_sensor_dict(sensors_list):
    """Return a dict of available sensors (from a list of W1ThermSensor data records) formatted per example dict.
    TODO determine if precision can be read or can only be set."""
    # load the existing sensors file
    existing = retrieve_json(SENSOR_JSON_FILE)    
    results = {}
    if sensors_list != None:
        for sensor in sensors_list:
            if sensor.id in existing.keys():
                results[sensor.id] = existing[sensor.id]
            else:
                results[sensor.id] = EXAMPLE_DICT["Device ID HEX value goes here"].copy()
                results[sensor.id]["device type"] = sensor.type
    else:
        # TODO log error
        print(f'Sensor list is None.')
    return results



@logger.catch
def get_active_sensor_list():
    """Read temp sensing devices and return list of sensors responding."""
    # TODO log start of program
    # create an instance of the monitoring class
    try:
        sensor = W1ThermSensor()
    except errors.NoSensorFoundError as error:
        # TODO log error
        print("No sensors found {error}")
        sensor = None

    available_sensors = []
    if sensor != None:
        available_sensors = sensor.get_available_sensors()
        if available_sensors == None:
            # TODO log error getting sensors
            print("no sensors reporting")
    else:
        # TODO log no sensor object available
        print(f'No sensor object available')
    # TODO log function end
    return available_sensors


@logger.catch
def get_humidity_reading():
    """Reads a DHT device connected to this server."""
    # Sensor should be set to Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
    sensor = Adafruit_DHT.DHT11
    # Example using a Raspberry Pi with DHT sensor connected to GPIO23.
    pin = 25
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, celsius = Adafruit_DHT.read_retry(sensor, pin)
    temperature = (celsius * 9/5) + 32
    # Note that sometimes you won't get a reading and the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor). If this happens try again!
    return (temperature, humidity)



if __name__ == '__main__':
    local_temp_and_humid = get_humidity_reading()
    print(f'{local_temp_and_humid=}')
    sensors = get_active_sensor_list()
    print(f'{len(sensors)} sensors reporting.')
    sensors_dict = build_sensor_dict(sensors)
    print(f'{len(sensors)} items in sensor dict.')
    current_temps = get_current_temps(sensors_dict)
    print(f'{current_temps=}')
