"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, time, date
from w1Therm import read_temperatures, time_now
from dht11_test import get_humidity
from LCD_statusd import start_LCD_daemon

from loguru import logger
import time
from csv_functions import write_csv
from CONSTANTS import *


@logger.catch
def main_data_gathering_loop():
    time_delay = 0
    while True:

        sensors_reporting = read_temperatures()

        print(f"{time_now()} Updating readings of {len(sensors_reporting['responding'])} sensors...")
        write_csv(sensors_reporting["all records"])        
        # print("Sleeping 1 second...")
        time.sleep(1)
    return


@logger.catch
def main():
    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    # TODO find a way to make IP address discoverable without attaching a monitor to the pi
    # TODO maybe use a common name that can be typed into a web browser on the same intranet
    print("Start main recorder.")
    sensors_reporting = read_temperatures()
    # print(f"\nsensors reporting:\n{sensors_reporting}")
    if (sensors_reporting["all records"] == None) or (
        sensors_reporting["all records"] == {}
    ):
        # TODO log error
        print("no sensors error")
    else:
        print(f"{time_now()} ::: {len(sensors_reporting['responding'])} sensors found.")

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon()  # this function currently exits quickly and never runs again
    main_data_gathering_loop()  # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main()
