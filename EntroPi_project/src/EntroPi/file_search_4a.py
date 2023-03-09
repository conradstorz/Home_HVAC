"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""

import io
import os
import csv
import tempfile
import zipfile
from pathlib import Path
from loguru import logger
import pytest
from hypothesis import given, strategies as st

@logger.catch
def select_csv_file():
    csv_files = find_csv_files()  # 1. Find all CSV files
    csv_files += find_csv_files_in_zips()  # 2. Find all CSV files in ZIP files
    csv_files = sort_csv_files_by_modification_time(csv_files)  # 3. Sort CSV files by modification time
    display_csv_files(csv_files)  # 4. Display the list of CSV files
    selected_file = get_selected_file(csv_files)  # 5. Get user input for the selected file
    logger.info(f'{selected_file=}')
    if selected_file is None:
        return None
    temp_file = extract_csv_data(selected_file)  # 6. Extract the selected CSV file if it is in a ZIP file
    logger.info(f'{temp_file=}')
    return write_to_temp_file(temp_file)  # 7. Return the name of the temporary file containing the CSV data

@logger.catch
def find_csv_files():
    csv_files = []
    for file in Path().glob("*"):
        if file.is_file() and file.name.endswith(".csv"):
            csv_files.append(file)
    return csv_files

@logger.catch
def find_csv_files_in_zips():
    csv_files = []
    for file in Path().glob("*"):
        if file.is_file() and file.name.endswith(".zip"):
            with zipfile.ZipFile(file, 'r') as zip:
                for zip_file in zip.namelist():
                    if zip_file.endswith(".csv"):
                        csv_files.append(f"{file}!{zip_file}")
    return csv_files

@logger.catch
def sort_csv_files_by_modification_time(csv_files):
    return sorted(csv_files, key=lambda f: get_modification_time(f), reverse=True)

@logger.catch
def display_csv_files(csv_files):
    if not csv_files:
        print("No CSV files found.")
        return
    print("Select a CSV file to process:")
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {get_displayable_name(file)}")

@logger.catch
def get_selected_file(csv_files):
    while True:
        choice = input("Enter the number of the CSV file to plot (or q to quit): ")
        if choice.lower() == "q":
            exit()
        try:
            choice = int(choice)
            if 1 <= choice <= len(csv_files):
                return csv_files[choice-1]
        except ValueError:
            pass
        print('Invalid choice. Please try again.')
    return None



@logger.catch
def extract_csv_data(selected_file):
    if "!" in str(selected_file):
        zip_file, csv_file = str(selected_file).split("!")
        logger.info(f'{csv_file=}')
        with zipfile.ZipFile(zip_file, 'r') as zip:
            with zip.open(csv_file) as csvfile:
                with tempfile.NamedTemporaryFile(mode='w+', newline='', encoding='utf-8', delete=False) as temp_file:
                    temp_file.write(csvfile.read().decode())
                    temp_file.seek(0)
                    temp_path = Path(temp_file.name)
    else:
        with open(selected_file, 'r') as csvfile:
            with tempfile.NamedTemporaryFile(mode='w+', newline='', encoding='utf-8', delete=False) as temp_file:
                temp_file.write(csvfile.read())
                temp_file.seek(0)
                temp_path = Path(temp_file.name)
    try:
        csv_reader = csv.reader(temp_path.open())
        headers = next(csv_reader)
        rows = list(csv_reader)
        if not headers or not rows:
            raise Exception("Empty CSV file.")
    except Exception as e:
        print(f"Error parsing CSV data: {e}")
        return None
    return temp_path



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
        logger.debug(f'get_name() from a string: {file}')
        if '!' in file:
            zipname, filename = file.split('!')
            return filename
        else:
            return os.path.basename(file)
    elif isinstance(file, Path):
        logger.debug(f'get_name() from a path object: {file}')
        return file.name
    else:
        raise TypeError("Argument must be a string or a Path object")
"""this is not ready yet. it needs not to send test inputs that contain '!'
@given(file=st.one_of(st.text(min_size=1, max_size=100),
                      st.builds(Path, st.text(min_size=1, max_size=100))))
def test_get_name(file):
    expected_output = os.path.basename(file)
    assert get_name(file) == expected_output
"""

@logger.catch
def get_displayable_name(file):
    if isinstance(file, str):
        if '!' in file:
            zipname, filename = file.split('!',1)
            return f"{zipname} ({filename})"
        else:
            return file
    elif isinstance(file, Path):
        return file.name
    else:
        raise TypeError("Argument must be a string or a Path object")


@given(zipname=st.from_regex(r'[^!]*[^\s!]', fullmatch=True),
       filename=st.from_regex(r'[^!]*[^\s!]', fullmatch=True))
def test_get_displayable_name(zipname, filename):
    file = f"{zipname}!{filename}"
    result = get_displayable_name(file)
    expected = f"{zipname} ({filename})"
    assert result == expected

@logger.catch
def write_to_temp_file(temp_file: Path) -> str:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        try:
            with open(temp_file, 'r') as input_file:
                f.write(input_file.read())
            return f.name
        except Exception as e:
            logger.error(f"Error writing data to temporary file: {e}")
            return None


if __name__ == '__main__':
    print(f'File saved as: {select_csv_file()}')
    