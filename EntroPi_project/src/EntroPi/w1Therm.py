"""Proof of concept code for working with temperature sensors through a headless RaspberryPi.
"""
# load needed modules
from w1thermsensor import W1ThermSensor, Unit, errors
from datetime import datetime
import json
from json.decoder import JSONDecodeError
from loguru import logger
from CONSTANTS import *


@logger.catch
def time_now():
    return datetime.now().strftime("%Y/%m/%d-%H:%M:%S")


@logger.catch
def build_sensor_dict(sensors_list):
    """Return a dict of available sensors formatted per example dict.
    TODO determine if precision can be read or can only be set."""
    print(f'Start build sensor dict.')
    results = {}
    print(f'Sensor list: {sensors_list}')
    if sensors_list != None:
        print(f'Sensor list: {sensors_list}')
        for sensor in sensors_list:
            print(f'processing sensor: {sensor}')
            try:
                current_reading = sensor.get_temperature()
            except (errors.SensorNotReadyError, errors.ResetValueError) as error:
                # TODO log error
                current_reading = None
            results[sensor.id] = EXAMPLE_DICT["Device ID HEX value goes here"].copy()
            results[sensor.id]["device type"] = sensor.type
            results[sensor.id]["temperature"] = current_reading
            results[sensor.id]["most recent date accessed"] = time_now()
    else:
        # TODO log error
        pass
    return results


@logger.catch
def retrieve_json(sensor_file):
    """JSON file is a key/value file of device IDs of previously found devices.
    key = Hex Address of device
    value = dict of device attributes.
        Attributes include:
            Device Type,
            Accuracy value, # for 18B20 devices 9-12 bits
            First 'seen' date,
            Most recent date accessed and value,
            Highest value and date,
            Lowest value and date
    """
    try:
        with open(sensor_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, JSONDecodeError) as error:
        # TODO log this error: print(f"Error with JSON file: {error}")
        data = {}
    return data


@logger.catch
def update_minmax_records(old_readings_from_devices, new_readings_from_devices):
    """Old readings is a dict of device IDs with an associated dict of observed values from device.
    Likewise, New readings is a dict of devie IDs and their associated values dicts.
    New devices will be added to the old. Pre-existing records will be updated."""

    @logger.catch
    def compare_device_readings(old_reading, new_reading):
        """Compare a single device's record dict to it's old record and update as needed.
        This function does not know what the device ID is. It is only working with the
        dict of values associated with a device."""
        for key, value in new_reading.items():
            current_device_temperature_reading = new_reading["temperature"]
            # TODO log beginning of device value comparrison
            if current_device_temperature_reading != None:
                if key in old_reading:
                    if key == "most recent date accessed":
                        if new_reading["most recent date accessed"] != None:
                            old_reading[key] = new_reading["most recent date accessed"]
                            old_reading[
                                "temperature"
                            ] = current_device_temperature_reading
                    if key == "accuracy value" and old_reading[key] != value:
                        # TODO log change in precision
                        old_reading[key] = value
                    if key == "highest value":
                        if (old_reading[key] == None) or (
                            old_reading[key] < current_device_temperature_reading
                        ):
                            # TODO log change in highest value
                            old_reading[key] = current_device_temperature_reading
                            old_reading["highest date"] = new_reading["highest date"]
                    if key == "lowest value":
                        if (old_reading[key] == None) or (
                            old_reading[key] > current_device_temperature_reading
                        ):
                            # TODO log change in lowest value
                            old_reading[key] = current_device_temperature_reading
                            old_reading["lowest date"] = new_reading["lowest date"]
                else:
                    # TODO log addition of new monitoring value
                    old_reading[key] = value
            else:
                # TODO log error that device did not contain valid info
                pass
        # TODO log completion of updating individual device values.
        return old_reading

    # loop over the dict of devices, This is the dict of device IDs and their associated value dicts.
    if new_readings_from_devices == None:
        # TODO log error
        print('error')
    else:
        for key, new_value in new_readings_from_devices.items():
            # TODO log beginning of updating of device
            if key not in old_readings_from_devices:
                # TODO log discovery of new device
                old_readings_from_devices[key] = new_value  # add missing or new device
            else:
                # this device has a previous record and it needs to be updated.
                old_value = old_readings_from_devices[key]
                # replace dict record with updated values
                old_readings_from_devices[key] = compare_device_readings(old_value, new_value)
    # TODO log completion of updating devices record
    return old_readings_from_devices


@logger.catch
def write_json(file, sensor_data_dict):
    """Accept a dictionary that describe sensors and
    write out to the specified JSON file."""

    # Save the updated JSON file
    with open(file, "w") as outfile:
        json.dump(sensor_data_dict, outfile)
    return


def update_device_definitions(reported_devices):
    """Compare reported devices to the existing JSON file describing known devices. Update accordingly.
        User of the system may choose to make changes to the JSON file from the system commandline or other access.
        These changes are normally just to update the description of what is being monitored by each device."""
    print(f'no function yet for update device definitions')
    return reported_devices


@logger.catch
def read_temperatures():
    # TODO log start of program
    print('Start function read temps.')
    # create an instance of the monitoring class
    try:
        sensor = W1ThermSensor()
    except errors.NoSensorFoundError as error:
        # TODO log error
        print('No sensors found {error}')
        sensor = None
    # recover json file of sensors
    print(f'Get JSON file')
    existing_device_records = retrieve_json(SENSOR_JSON_FILE)
    available_sensors = []
    print(f'SENSOR: {sensor}')
    if sensor != None:
        print(f'Get available sensors')
        available_sensors = sensor.get_available_sensors()
        print(f'AVAILABLE: {available_sensors}')
        if available_sensors != None:
            print(f'Process sensors')
            # TODO read sensor_update_file.JSON for device IDs and location names. Check for changes to update sensor_file.JSON
            # sensor_definition.JSON can be modified by the user to re-locate sensor locations or define initial locations.
            available_sensors = update_device_definitions(available_sensors)            
            # create the dictionary of sensors and their associated values
            active_sensor_data_dict = build_sensor_dict(available_sensors)
            # update readings and add missing devices
            combined_data = update_minmax_records(
                existing_device_records, active_sensor_data_dict
            )
            write_json(SENSOR_JSON_FILE, combined_data)
        else:
            # TODO log error getting sensors
            print('no sensors reporting')
    else:
        # TODO log no sensors reporting error
        # default the output to previous JSON records
        combined_data = existing_device_records       
    # TODO log function end
    return {"all records": combined_data, "responding": available_sensors}


@logger.catch
def main():
    all, responding = read_temperatures().items()
    print(all)
    print(f"\n\nOnly devices responding:\n{responding}")


if __name__ == "__main__":
    main()
