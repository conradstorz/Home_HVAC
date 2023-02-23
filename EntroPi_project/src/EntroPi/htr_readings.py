"""Proof of concept code for working with temperature sensors through a headless RaspberryPi.
"""
# load needed modules
from datetime import datetime, timedelta, time, date
from loguru import logger
from CONSTANTS import retrieve_json
from CONSTANTS import write_json
from CONSTANTS import SENSOR_DEFINITIONS
from CONSTANTS import SENSOR_JSON_FILE
from CONSTANTS import TEMP_AND_HUMIDITY_FILE
from CONSTANTS import MIN_WEATHER_URL_UPDATE_INTERVAL
from CONSTANTS import DATE_FORMAT_AS_STRING
from CONSTANTS import ZIPCODE
from CONSTANTS import EXAMPLE_DICT
from rotate_csv_and_compress import compress_local_csv
from open_weather_map import get_local_conditions
from w1thermDevices import get_current_temps
from w1thermDevices import build_sensor_dict
from w1thermDevices import get_active_sensor_list
from w1thermDevices import get_humidity_reading



@logger.catch
def read_temperatures():
    """Read temp and humidity sensing devices, local outside weather conditions and then update 
        readings into permanent device status file (JSON)"""
    # TODO log start of program
    # recover json file of sensors
    existing_device_records = retrieve_json(SENSOR_JSON_FILE)    
    # get local conditions
    local_data = {}
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
        logger.debug(f'{combined_data=}')
        write_json(SENSOR_JSON_FILE, combined_data)
    else:
        # TODO log error getting sensors
        logger.info("no sensors reporting")
        combined_data = {}
    return combined_data


@logger.catch
def update_temp_and_humidity():
    """Check time delay and get download from OpenWeather.com if time is right."""
    data = retrieve_json(TEMP_AND_HUMIDITY_FILE)
    # see if it is time to update the local weather conditions
    current_time = datetime.now() # This reading needs to be a datetime not a datestring
    if "Last weather update" not in data.keys():
        # entry doen't exist, create. Set time to past interval.
        last_update = current_time - MIN_WEATHER_URL_UPDATE_INTERVAL
        data["Last weather update"] = last_update.strftime(DATE_FORMAT_AS_STRING)
    else:
        last_update = data["Last weather update"]
        try:
            # derive datetime object from datestring
            last_update = datetime.strptime(last_update, DATE_FORMAT_AS_STRING)
        except TypeError as error:
            # entry can't be parsed, create. Set time to past interval.
            last_update = current_time - MIN_WEATHER_URL_UPDATE_INTERVAL
            data["Last weather update"] = last_update.strftime(DATE_FORMAT_AS_STRING)
        if current_time - last_update >= MIN_WEATHER_URL_UPDATE_INTERVAL:
            # time to poll external website.
            data["Last weather update"] = current_time.strftime(DATE_FORMAT_AS_STRING)            
            
            # update the local weather conditions, get current temp and humidity
            outside_temperature, outside_humidity = get_local_conditions(zipcode=ZIPCODE)
            logger.info(f'Outdoor temp is: {outside_temperature}')
            logger.info(f'Outdoor humidity is: {outside_humidity}')
            data["Last outside temperature"] = outside_temperature
            data["Last outdoor humidity"] = outside_humidity
            
            # read local humidity device attached to the device this program is running on.
            data["Temperature at device"], data["Humidity at device"] = get_humidity_reading()
            logger.info(f'Humidity at device is: {data["Humidity at device"]}')
            # TODO write to CSV, formatted same as any other device
            existing_records = retrieve_json(SENSOR_JSON_FILE) 
            for k,v in data.items():
                # make a freah copy of the deafults
                examp = EXAMPLE_DICT['Device ID HEX value goes here'].copy()
                # put this measurement into the dict
                examp['device location'] = k
                examp['most recent date accessed'] = data["Last weather update"]
                examp['temperature'] = v
                # call UPDATE function to track min/max values
                # TODO expand UPDATE function to be more easily useful for cases like these
                # examp = update(examp, existing_records[k])
                # write to CSV
                
            # TODO send_to_thingspeak(latest readings)
            
            # CSV files need to be compressed periodically
            compress_local_csv()
        else:
            last_update = current_time - MIN_WEATHER_URL_UPDATE_INTERVAL
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
        logger.info('Error. Device response was invalid.')
    else:       
        # TODO log beginning of device value comparrison
        for description, observed_value in new_reading.items():

            if description in COPY_REGARDLESS:
                output[description] = observed_value
            else:
                if description not in old_reading:
                    # TODO log addition of new monitoring value
                    logger.info(f'{description} was not previously monitored.')
                else:
                    # check for new highest reading
                    if description == "highest value":
                        if (old_reading["highest value"] == None) or (
                            old_reading["highest value"] < new_reading["temperature"]
                        ):
                            # TODO log change in highest value
                            output["highest value"] = new_reading["temperature"]
                            output["highest date"] = new_reading["most recent date accessed"]
                            logger.info(f'{new_reading["device location"]} {old_reading["highest value"]} New highest reading recorded. {new_reading["temperature"]}')
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
                            logger.info(f'{new_reading["device location"]} {old_reading["lowest value"]} New lowest reading recorded. {new_reading["temperature"]}')
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
        logger.info("error")
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
    logger.debug(f"Begin updating device location names if needed.")
    output = {}
    # load sensor definitions file
    definitions = retrieve_json(SENSOR_DEFINITIONS)
    # load the existing sensors file
    existing = retrieve_json(SENSOR_JSON_FILE)
    # loop over reported devices looking for matching device IDs
    logger.debug(f'Comparing reporting devices to definitions file looking for changes.')
    for deviceID, details in reported_devices_dict.items():
        logger.debug(f'{reported_devices_dict[deviceID]=}')
        output[deviceID] = details
        # check for device updates from user.
        if deviceID not in definitions.keys():
            logger.info(f"Key not found in location definitions file. {deviceID=}")
            logger.info(f"Nothing to do for this device.")
        else:
            # check to see if deivce was previously identified.
            if deviceID in existing.keys():
                # device was previously identified
                old_location = existing[deviceID]["device location"]
                if old_location != definitions[deviceID]["device location"]:
                    # update description of device location
                    output[deviceID]["device location"] = definitions[deviceID]["device location"]
                    output[deviceID]["accuracy value"] = definitions[deviceID]["accuracy value"]
                    logger.info(f'{deviceID=} updated name to: {definitions[deviceID]["device location"]} :::from::: {old_location}')
    write_json(SENSOR_JSON_FILE, output)
    logger.info(f"End device updating")
    return output


@logger.catch
def main():
    responding = read_temperatures()
    logger.info(f"Only devices responding:{responding.keys()}")
    for k,v in responding.items():
        logger.info(k)
        for i in v.items():
            logger.info(f'{i}')

if __name__ == "__main__":
    main()
