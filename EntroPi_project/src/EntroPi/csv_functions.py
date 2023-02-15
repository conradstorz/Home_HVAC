from loguru import logger
from datetime import datetime
import csv
from pathlib import Path
from CONSTANTS import *


@logger.catch
def generate_csv_filename(basename=None):
    if basename == None:
        basename = "BASENAME"
    return f'{datetime.now().strftime("%Y%m%d")}{basename}.csv'


@logger.catch
def write_csv(device_data, directory="."):
    """Takes a dict and an optional directory= arguments and writes to a file
        with todays date as part of the filename. Each day the old filename
        is abandoned and a new filename is started."""
    # Open the output CSV file and write 'the results
    logger.debug(f"Begin saving data...")
    logger.debug(f"device_data:{device_data}")
    if device_data != None:
        if device_data != {}:
            first_key = list(device_data)[0]
            # grab the first entry as an example
            first_device_values = device_data[first_key]
            # retrieve keys from nested dictionaries
            fieldnames = (first_device_values.keys())  
            logger.debug(f"CSV file fieldnames:{fieldnames}")
            out_csv = Path(generate_csv_filename(BASENAME_CSV_FILE))
            logger.debug(f'does CSV file exist: {out_csv.exists()}')
            # check if file exists and write headers if new file
            if not out_csv.exists():
                logger.info(f"CSV file does not exist. Creating...")
                logger.info(f"CSV file fieldnames:{fieldnames}")
                with open(out_csv, "w", newline="") as h:
                    writer = csv.DictWriter(h, fieldnames=fieldnames)
                    writer.writeheader()
            logger.debug(f'Appending file CSV data.')
            with open(out_csv, "a", newline="") as h:
                writer = csv.DictWriter(h, fieldnames=fieldnames)
                # Write a row for each location
                for device, values in device_data.items():
                    writer.writerow(values)
            logger.info(f"Output file saved as {out_csv.name}.")
        else:
            # TODO log error
            logger.info("Empty dict unexpected.")
    else:
        # TODO log error
        logger.info("No data to add to CSV file.")
    return
