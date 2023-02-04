"""Proof of concept code for working with temperature sensors through a headless RaspberryPi.
"""
# load needed modules
from w1thermsensor import W1ThermSensor, Sensor, Unit, errors
from datetime import datetime, timedelta, time, date
import json
from json.decoder import JSONDecodeError
from loguru import logger
from CONSTANTS import *
from rotate_csv_and_compress import compress_local_csv
from open_weather_map import get_temp_and_humidity


@logger.catch
def time_now():
    return datetime.now().strftime("%Y/%m/%d-%H:%M:%S")


@logger.catch
def get_current_temps(sensor_dict):
    results = {}
    for deviceID, details in sensor_dict.items():
        results[deviceID] = sensor_dict[deviceID].copy()
        # print(f"\nreading sensor: {deviceID}")
        try:
            sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=f"{deviceID}")
            temperature_in_celsius = sensor.get_temperature()
            current_reading = temperature_in_celsius
        except (errors.SensorNotReadyError, errors.ResetValueError) as error:
            # TODO log error
            print(f'Error reading sensor: {deviceID} with error: {error}')
            current_reading = None
        results[deviceID]["temperature"] = current_reading
        results[deviceID]["most recent date accessed"] = time_now()
    return results


@logger.catch
def build_sensor_dict(sensors_list):
    """Return a dict of available sensors (from a list of W1ThermSensor data records) formatted per example dict.
    TODO determine if precision can be read or can only be set."""
    # print(f'\nStart build sensor dict from: {sensors_list}')
    # load the existing sensors file
    existing = retrieve_json(SENSOR_JSON_FILE)    
    results = {}
    if sensors_list != None:
        for sensor in sensors_list:
            # print(f"\nprocessing sensor: {sensor}")
            if sensor.id in existing.keys():
                results[sensor.id] = existing[sensor.id]
            else:
                results[sensor.id] = EXAMPLE_DICT["Device ID HEX value goes here"].copy()
                results[sensor.id]["device type"] = sensor.type
    else:
        # TODO log error
        print(f'Sensor list is None.')
    # print(f'\n{results=}')
    return results


@logger.catch
def retrieve_json(file_name):
    """JSON file is a key/value file of device IDs of previously found devices."""
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, JSONDecodeError) as error:
        # TODO log this error: print(f"Error with JSON file: {error}")
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


@logger.catch
def get_temp_and_humidity():
    """Check time delay and get download from OpenWeather.com if time is right."""
    data = retrieve_json(TEMP_AND_HUMIDITY_FILE)
    # see if it is time to update the local weather conditions
    current_time = datetime.now()
    if "last_weather_update" not in data.keys():
        # previous record does not exist, create.
        data["last_weather_update"] = current_time.strftime(DATE_FORMAT_AS_STRING)
        data["last_outside_temperature"] = None
        data["last_outdoor_humidity"] = None
    else:
        last_update = data["last_weather_update"]
        last_update = datetime.strptime(last_update, DATE_FORMAT_AS_STRING)
        if current_time - last_update >= MIN_WEATHER_URL_UPDATE_INTERVAL:
            # TODO Compress_CSV_files() # CSV files need to be compressed periodically
            compress_local_csv()
            # update the local weather conditions
            data["last_weather_update"] = current_time.strftime(DATE_FORMAT_AS_STRING)
            # get current temp and humidity
            outside_temperature, outside_humidity = get_temp_and_humidity(zipcode=ZIPCODE)
            print(f'Outdoor temp is: {outside_temperature}')
            print(f'Outdoor humidity is: {outside_humidity}')
            data["last_outside_temperature"] = outside_temperature
            data["last_outdoor_humidity"] = outside_humidity
            # TODO send_to_thingspeak(latest readings)
    write_json(TEMP_AND_HUMIDITY_FILE, data)
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
                            old_reading["temperature"] = current_device_temperature_reading
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
        print("error")
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
                old_readings_from_devices[key] = compare_device_readings(
                    old_value, new_value
                )
    # TODO log completion of updating devices record
    return old_readings_from_devices


def update_device_definitions(reported_devices_dict):
    """Compare reported devices to the existing JSON file describing known devices. Update accordingly.
    User of the system may choose to make changes to the JSON file from the system commandline or other access.
    These changes are normally just to update the description of what is being monitored by each device."""
    # print(f"\nBegin updating device location names if needed.")
    nothing_changed = True
    output = {}
    # load sensor definitions file
    definitions = retrieve_json(SENSOR_DEFINITIONS)
    # load the existing sensors file
    existing = retrieve_json(SENSOR_JSON_FILE)
    # loop over reported devices looking for matching device IDs
    # print(f'Comparing reporting devices to definitions file looking for changes.')
    for deviceID, details in reported_devices_dict.items():
        # print(f'\n{reported_devices_dict[deviceID]=}')
        output[deviceID] = details
        # check for device updates from user.
        if deviceID not in definitions.keys():
            print(f"Key not found in location definitions file. {deviceID=}")
            print(f"Nothing to do for this device.")
        else:
            # print(f'\n{definitions[deviceID]=}')
            # check to see if deivce was previously identified.
            if deviceID in existing.keys():
                # print(f'\n{existing[deviceID]=}')
                # device was previously identified
                old_location = existing[deviceID]["device location"]
                if old_location != definitions[deviceID]["device location"]:
                    # update description of device location
                    nothing_changed = False
                    output[deviceID]["device location"] = definitions[deviceID]["device location"]
                    output[deviceID]["accuracy value"] = definitions[deviceID]["accuracy value"]
                    print(f'\n{deviceID=} updated name to: {definitions[deviceID]["device location"]} :::from::: {old_location}')
                else:
                    # device location description is a match
                    pass
            else:
                # device was not in existing record. Adding to the existing record dict.
                print(f'New device found. Adding to existing devices record.')
                existing[deviceID] = details
                nothing_changed = False
    if nothing_changed:
        pass
    else:
        # update permanent record
        write_json(SENSOR_JSON_FILE, existing)
    # print(f"\nEnd device update")
    return output


@logger.catch
def read_temperatures():
    # TODO log start of program
    # print("Start function read temps.")
    # create an instance of the monitoring class
    try:
        sensor = W1ThermSensor()
        # print(f"\nSENSOR: {sensor}")
    except errors.NoSensorFoundError as error:
        # TODO log error
        print("No sensors found {error}")
        sensor = None
    # recover json file of sensors
    # print(f"\nGet JSON file")
    existing_device_records = retrieve_json(SENSOR_JSON_FILE)
    available_sensors = []
    # print(f'\nexisting devices: {existing_device_records}')
    if sensor != None:
        # print(f"\nGet available sensors")
        available_sensors = sensor.get_available_sensors()
        # print(f'\nAVAILABLE: {available_sensors}')
        if available_sensors != None:
            # print(f"\nProcess sensors")
            # create the dictionary of sensors from a list of sensor devices in the W1ThermSensor format
            active_sensor_data_dict = build_sensor_dict(available_sensors)
            # poll sensors for current data
            active_sensor_data_dict = get_current_temps(active_sensor_data_dict)
            # sensor_definition.JSON can be modified by the user to re-locate sensor locations or define initial locations.
            # print(f'\n{active_sensor_data_dict=}')
            updated_dict = update_device_definitions(active_sensor_data_dict)
            # print(f'\n{updated_dict=}')
            # update readings and add missing devices
            combined_data = update_minmax_records(existing_device_records, updated_dict)
            write_json(SENSOR_JSON_FILE, combined_data)
        else:
            # TODO log error getting sensors
            print("no sensors reporting")
    else:
        # TODO log no sensor object available
        # default the output to previous JSON records
        combined_data = existing_device_records
    # get local conditions
    local_data = get_temp_and_humidity()
    # TODO log function end
    return {"all records": combined_data, "responding": available_sensors, "local_conditions": local_data}


@logger.catch
def main():
    all, responding = read_temperatures().items()
    print(all)
    print(f"\n\nOnly devices responding:\n{responding}")


if __name__ == "__main__":
    main()
