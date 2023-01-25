from loguru import logger
from datetime import datetime
import csv
from pathlib import Path


@logger.catch
def generate_csv_filename(basename = None):
    if basename == None:
        basename = "BASENAME"
    return f'{datetime.now().strftime("%Y%m%d")}{basename}.csv'


@logger.catch
def write_csv(device_data, directory="."):
    # Open the output CSV file and write 'the results
    print(f"Begin saving data: \ndevice_data:\n{device_data}\n")
    if device_data != None:
        if device_data != {}:
            first_key = list(device_data)[0]
            first_device_values = device_data[first_key]
            fieldnames = first_device_values.keys()  # retrieve keys from nested dictionaries
            print(f"CSV file fieldnames:\n{fieldnames}\n")
            out_csv = Path(generate_csv_filename())
            # check if file exists and write headers if new file
            if not out_csv.exists:
                print(f'CSV file does not exist. Creating...')
                with open(out_csv, "w", newline="") as h:
                    writer = csv.DictWriter(h, fieldnames=fieldnames)
                    writer.writeheader()
            else:
                with open(out_csv, "a", newline="") as h:
                    writer = csv.DictWriter(h, fieldnames=fieldnames)
                    # Write a row for each location
                    for device, values in device_data.items():
                        writer.writerow(values)
            print(f"Output file saved as {out_csv.name}.")
        else:
            # TODO log error
            print('Empty dict unexpected.')
    else:
        # TODO log error
        print('No data to add to CSV file.')
    return