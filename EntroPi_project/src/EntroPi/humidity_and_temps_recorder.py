"""A self contained and systemd service package for monitoring temperatures"""
__version__ = "0.1"
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from htr_readings import read_temperatures
from LCD_statusd import start_LCD_daemon
from loguru import logger
import time
from csv_functions import write_csv
from CONSTANTS import *


@logger.catch
def main_data_gathering_loop(ENV_VARS):
    while True:
        sensors_reporting = read_temperatures(ENV_VARS)
        if sensors_reporting != None:
            logger.info(f"Updating readings of {len(sensors_reporting)} sensors...")
            write_csv(sensors_reporting)        
        else:
            logger.error(f'Nonetype returned from "Read_temperatures" function.')
        logger.debug("Sleeping 1 second...")
        time.sleep(1)
    return


@logger.catch
def main(ENV_VARS_DICT):
    """Due to the environment of this script being different depending on how it is run,
    the environment variables found in '.bashrc' in the home directory are loaded by the
    main EntroPi script and then fed into this function."""

    # TODO make a seperate script webserver that displays all details and offers ability to rename sensors
    
    logger.info("Start main recorder.")
    
    sensors_reporting = read_temperatures(ENV_VARS_DICT)
    logger.debug(f"sensors reporting:{sensors_reporting}")
    if (sensors_reporting == []) or (sensors_reporting == None):
        # TODO log error
        logger.info("no sensors error")
    else:
        logger.info(f"{time_now_string()} ::: {len(sensors_reporting)} sensors found.")

    # TODO see if these next 2 functions can be runtogether by some means of multitasking.
    start_LCD_daemon()  # this function currently exits quickly and never runs again
    main_data_gathering_loop(ENV_VARS_DICT)  # process stays here until crash or reboot
    return


if __name__ == "__main__":
    main({})
