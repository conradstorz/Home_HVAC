"""Proof of concept code for working with temperature sensors through a headless RaspberryPi.
"""
# load needed modules
from w1thermsensor import W1ThermSensor, Sensor, Unit, errors
from datetime import datetime, timedelta, time, date
import json
from json.decoder import JSONDecodeError
from loguru import logger
from CONSTANTS import time_now_string
from CONSTANTS import retrieve_json
from CONSTANTS import write_json
from CONSTANTS import SENSOR_DEFINITIONS
from CONSTANTS import SENSOR_JSON_FILE
from CONSTANTS import TEMP_AND_HUMIDITY_FILE
from CONSTANTS import EXAMPLE_DICT
from CONSTANTS import MIN_WEATHER_URL_UPDATE_INTERVAL
from CONSTANTS import DATE_FORMAT_AS_STRING
from CONSTANTS import ZIPCODE
from rotate_csv_and_compress import compress_local_csv
from open_weather_map import get_local_conditions
from w1thermDevices import get_current_temps
from w1thermDevices import build_sensor_dict
from w1thermDevices import get_active_sensor_list



@logger.catch
def read_temperatures():
    """Read temp and humidity sensing devices, local outside weather conditions and then update 
        readings into permanent device status file (JSON)"""
    # TODO log start of program
    # recover json file of sensors
    existing_device_records = retrieve_json(SENSOR_JSON_FILE)    
    # get local conditions
    local_data = update_temp_and_humidity()
    # get inside humidity
    inside_humidity = 0
    local_data['inside humidity'] = inside_humidity      

    available_sensors = get_active_sensor_list()

    if available_sensors != []:
        # create the dictionary of sensors from a list of sensor devices in the W1ThermSensor format
        active_sensor_data_dict = build_sensor_dict(available_sensors)
        # poll sensors for current data
        current_sensor_data_dict = get_current_temps(active_sensor_data_dict)
        # sensor_definition.JSON can be modified by the user to re-locate sensor locations or define initial locations.
        # combine local data with sensor readings data
        updated_dict = update_device_definitions(current_sensor_data_dict)
        # update readings and add missing devices
        combined_data = update_minmax_records(existing_device_records, updated_dict)
        # print(f'{combined_data=}')
        write_json(SENSOR_JSON_FILE, combined_data)
    else:
        # TODO log error getting sensors
        print("no sensors reporting")
    return combined_data


@logger.catch
def update_temp_and_humidity():
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
            # CSV files need to be compressed periodically
            compress_local_csv()
            # update the local weather conditions
            data["last_weather_update"] = current_time.strftime(DATE_FORMAT_AS_STRING)
            # get current temp and humidity
            outside_temperature, outside_humidity = get_local_conditions(zipcode=ZIPCODE)
            print(f'Outdoor temp is: {outside_temperature}')
            print(f'Outdoor humidity is: {outside_humidity}')
            data["last_outside_temperature"] = outside_temperature
            data["last_outdoor_humidity"] = outside_humidity
            # TODO write to CSV and remove placing this data into each sensor entry
            # TODO send_to_thingspeak(latest readings)
    write_json(TEMP_AND_HUMIDITY_FILE, data)
    return data


@logger.catch
def compare_device_readings(old_reading, new_reading):
    """Compare a single device's record dict to it's old record and update as needed.
    This function does not care what the device ID is. It is only working with the
    dict of values associated with a device."""
    # TODO take outside readings off here. They will get entered at the time of reading
    COPY_REGARDLESS = ["device location","device type","accuracy value","first seen date",
        "most recent date accessed","temperature","outside temp","outside humidity","inside humidity"]
    output = {}
    if new_reading["temperature"] == None:
        # TODO log error that device did not contain valid info
        print('error')
    else:       
        # TODO log beginning of device value comparrison
        for description, observed_value in new_reading.items():

            if description in COPY_REGARDLESS:
                output[description] = observed_value
            else:
                if description not in old_reading:
                    # TODO log addition of new monitoring value
                    print(f'{description} was not previously monitored.')
                else:
                    # check for new highest reading
                    if description == "highest value":
                        if (old_reading["highest value"] == None) or (
                            old_reading["highest value"] < new_reading["temperature"]
                        ):
                            # TODO log change in highest value
                            output["highest value"] = new_reading["temperature"]
                            output["highest date"] = new_reading["most recent date accessed"]
                            print(f'{new_reading["device location"]} {old_reading["highest value"]} New highest reading recorded. {new_reading["temperature"]}')
                        else:
                            # retain the old reading
                            output["highest value"] = old_reading["highest value"]
                            output["highest date"] = old_reading["highest date"]

                    if description == "lowest value":
                        if (old_reading["lowest value"] == None) or (
                            old_reading["lowest value"] > new_reading["temperature"]
                        ):
                            # TODO log change in lowest value
                            output["lowest value"] = new_reading["temperature"]
                            output["lowest date"] = new_reading["most recent date accessed"]
                            print(f'{new_reading["device location"]} {old_reading["lowest value"]} New lowest reading recorded. {new_reading["temperature"]}')
                        else:
                            # retain the old reading
                            output["lowest value"] = old_reading["lowest value"]
                            output["lowest date"] = old_reading["lowest date"]
    # TODO log completion of updating individual device values.
    return output


@logger.catch
def update_minmax_records(old_readings_from_devices, new_readings_from_devices):
    """Old readings is a dict of device IDs with an associated dict of observed values from device.
    Likewise, New readings is a dict of device IDs and their associated values dicts.
    New devices will be added to the old. Pre-existing records will be updated."""
    # loop over the dict of devices, This is the dict of device IDs and their associated value dicts.
    output = {}
    if new_readings_from_devices == None:
        # TODO log error
        print("error")
    else:
        for new_device_ID, new_device_observations in new_readings_from_devices.items():
            # TODO log beginning of updating of device
            output[new_device_ID] = new_device_observations
            if new_device_ID in old_readings_from_devices:
                # this device has a previous record and it needs to be updated.
                old_device_observations = old_readings_from_devices[new_device_ID]
                # replace dict record with updated values
                output[new_device_ID] = compare_device_readings(old_device_observations, new_device_observations)
    # TODO log completion of updating devices record
    return output


@logger.catch
def update_device_definitions(reported_devices_dict):
    """Compare reported devices to the existing devices JSON file describing known devices. Update accordingly.
    User of the system may choose to make changes to the JSON file from the system commandline or other access.
    These changes are normally just to update the description of what is being monitored by each device.
    """
    # print(f"\nBegin updating device location names if needed.")
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
            # check to see if deivce was previously identified.
            if deviceID in existing.keys():
                # device was previously identified
                old_location = existing[deviceID]["device location"]
                if old_location != definitions[deviceID]["device location"]:
                    # update description of device location
                    output[deviceID]["device location"] = definitions[deviceID]["device location"]
                    output[deviceID]["accuracy value"] = definitions[deviceID]["accuracy value"]
                    print(f'{deviceID=} updated name to: {definitions[deviceID]["device location"]} :::from::: {old_location}')
    write_json(SENSOR_JSON_FILE, output)
    print(f"\nEnd device update")
    return output


@logger.catch
def main():
    responding = read_temperatures()
    print(f"\n\nOnly devices responding:\n{responding.keys()}")
    for k,v in responding.items():
        print(k)
        for i in v.items():
            print(f'{i}')

if __name__ == "__main__":
    main()
