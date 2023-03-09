"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""

import io
import os
import csv
from tempfile import NamedTemporaryFile
import zipfile
from pathlib import Path
from loguru import logger


@logger.catch
def select_csv_file():
    # Find all CSV files in the current directory and its subdirectories
    csv_files = []
    for file in Path().glob("*"):
        if file.is_file() and file.name.endswith(".csv"):
            csv_files.append(file)

    # Find all CSV files in ZIP files in the current directory and its subdirectories
    for file in Path().glob("*"):
        if file.is_file() and file.name.endswith(".zip"):
            with zipfile.ZipFile(file, 'r') as zip:
                for zip_file in zip.namelist():
                    if zip_file.endswith(".csv"):
                        csv_files.append(f"{file}!{zip_file}")

    # Sort the list of CSV files by modification time, with newest first
    csv_files = sorted(csv_files, key=lambda f: get_modification_time(f), reverse=True)

    # Display the list of CSV files
    if not csv_files:
        print("No CSV files found.")
        return None

    print("Select a CSV file to process:")
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {get_displayable_name(file)}")

    # Get user input for the selected file
    while True:
        choice = input("Enter the number of the CSV file to plot (or q to quit): ")
        if choice.lower() == "q":
            exit()
        try:
            choice = int(choice)
            if 1 <= choice <= len(csv_files):
                break
        except ValueError:
            pass
        print('Invalid choice. Please try again.')

    # Extract the selected CSV file if it is in a ZIP file
    selected_file = csv_files[choice-1]
    logger.debug(f'{selected_file=}')
    filename = get_name(selected_file)
    logger.debug(f'{filename=}')
    if "!" in filename:
        zip_file, csv_file = filename.split("!")
        with zipfile.ZipFile(zip_file, 'r') as zip:
            with zip.open(csv_file) as csvfile:
                temp_file = io.StringIO(csvfile.read().decode())
    else:
        with open(filename, 'r') as csvfile:
            temp_file = io.StringIO(csvfile.read())
    logger.debug(f'{temp_file=}')
    # Attempt to parse the CSV data to ensure it is valid
    try:
        csv_reader = csv.reader(temp_file)
        headers = next(csv_reader)
        rows = list(csv_reader)
        if not headers or not rows:
            raise Exception("Empty CSV file.")
    except Exception as e:
        print(f"Error parsing CSV data: {e}")
        return None

    # Return the name of the temporary file containing the CSV data
    return write_to_temp_file(temp_file.getvalue())

@logger.catch
def get_modification_time(file):
    if isinstance(file, str):
        if '!' in file:
            filepath = Path(file.split('!')[0])
        else:
            filepath = Path(file)
    elif isinstance(file, Path):
        filepath = file
    else:
        raise TypeError("Argument must be a string or a Path object")

    try:
        return os.path.getmtime(filepath)
    except OSError:
        return 0


@logger.catch
def get_name(file):
    if isinstance(file, str):
        if '!' in file:
            zipname, filename = file.split('!')
            return filename
        else:
            return file
    elif isinstance(file, Path):
        return file.name
    else:
        raise TypeError("Argument must be a string or a Path object")

@logger.catch
def get_displayable_name(file):
    if isinstance(file, str):
        if '!' in file:
            zipname, filename = file.split('!')
            return f"{zipname} ({filename})"
        else:
            return file
    elif isinstance(file, Path):
        return file.name
    else:
        raise TypeError("Argument must be a string or a Path object")



@logger.catch
def write_to_temp_file(data):
    try:
        temp_file = NamedTemporaryFile(mode='w', delete=False)
        temp_file.write(data)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"Error writing data to temporary file: {e}")
        return None


if __name__ == '__main__':
    print(f'File saved as: {select_csv_file()}')
    