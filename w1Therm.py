"""Proof of concept code for working with temperature sensors through a headless RaspberryPi.
"""
# load needed modules
from w1thermsensor import W1ThermSensor, Unit, errors
from datetime import datetime
import json
from json.decoder import JSONDecodeError

SENSOR_JSON_FILE = "w1devices.json"
TIME_NOW = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
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

def time_now():
    return datetime.now().strftime("%Y/%m/%d-%H:%M:%S")

def build_sensor_dict(sensors_list):
    """Return a dict of available sensors formatted per example dict.
    TODO determine if precision can be read or can only be set."""
    results = {}
    EXAMPLE = EXAMPLE_DICT["Device ID HEX value goes here"].copy()
    for sensor in sensors_list:
        try:
            current_reading = sensor.get_temperature()
        except (errors.SensorNotReadyError, errors.ResetValueError) as error:
            # TODO log error
            current_reading = None
        results[sensor.id] = EXAMPLE.copy()
        results[sensor.id]["device type"] = sensor.type
        results[sensor.id]["temperature"] = current_reading
        results[sensor.id]["most recent date accessed"] = time_now()
    return results


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
    # print(f'\n\nJSON data retreived:\n{data}\n')
    # TODO read sensor_update_file.JSON for device IDs and location names. Check for changes and update sensor_file.JSON
    # sensor_update can be modified by the user to re-locate sensor locations or define initial locations.
    return data


def update_minmax_records(old_readings_from_devices, new_readings_from_devices):
    """Old readings is a dict of device IDs with an associated dict of observed values from device.
    Likewise, New readings is a dict of devie IDs and their associated values dicts.
    New devices will be added to the old. Pre-existing records will be updated."""
    
    def compare_devices(old_reading, new_reading):
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
                            old_reading["temperature"] = current_device_temperature_reading
                    if key == "accuracy value" and old_reading[key] != value:
                        # TODO log change in precision
                        old_reading[key] = value
                    if key == "highest value":
                        if (old_reading[key] == None) or (old_reading[key] < current_device_temperature_reading):
                            # TODO log change in highest value
                            old_reading[key] = current_device_temperature_reading
                            old_reading["highest date"] = new_reading["highest date"]
                    if key == "lowest value":
                        if (old_reading[key] == None) or (old_reading[key] > current_device_temperature_reading):
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
    for key, value in new_readings_from_devices.items():
        # TODO log beginning of updating of device
        if key not in old_readings_from_devices:
            # TODO log discovery of new device
            old_readings_from_devices[key] = value # add missing or new device
        else:
            # this device has a previous record and it needs to be updated.
            old_readings_from_devices[key] = compare_devices(old_readings_from_devices[key], value)
    # TODO log completion of updating devices record
    return old_readings_from_devices


def write_json(file, sensor_data_dict):
    """Accept a dictionary that describe sensors and
    write out to the specified JSON file."""

    # Save the updated JSON file
    with open(file, "w") as outfile:
        json.dump(sensor_data_dict, outfile)
    return

def read_temperatures():
    # TODO log start of program

    # create an instance of the monitoring class
    try:
        sensor = W1ThermSensor()
    except errors.NoSensorFoundError as error:
        # TODO log error
        sensor = None

    # recover json file of sensors
    existing_device_records = retrieve_json(SENSOR_JSON_FILE)
    # default the output to JSON records
    combined_data = existing_device_records.copy()
    available_sensors = []
    if sensor != None:    
        available_sensors = sensor.get_available_sensors()
        # print(f"Available sensors are: {available_sensors}")

        """
        # loop through sensors and record their values
        sensor_dict_of_readings = {}
        for sensor in available_sensors:
            sensor_dict_of_readings[sensor.id] = sensor.get_temperature()
        """

        # create the dictionary of sensors and their associated values
        active_sensor_data_dict = build_sensor_dict(available_sensors)
        # print(f"Active sensors dict is:\n{active_sensor_data_dict}")

        # update readings and add missing devices
        combined_data = update_minmax_records(existing_device_records, active_sensor_data_dict)
        # print(f"JSON ready dict: \n{combined_data}")

        write_json(SENSOR_JSON_FILE, combined_data)

    # TODO log program exit
    return {'all records': combined_data, 'responding': available_sensors} 


def main():
    all, responding = read_temperatures().items()
    print(all)
    print(f'\n\nOnly devices responding:\n{responding}')
    



if __name__ == '__main__':
    main()