"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""

from tempfile import NamedTemporaryFile
import os
import io
import glob
import zipfile
import csv
from loguru import logger


@logger.catch
def choose_csv_file():
    csv_files = []
    for file in glob.glob("*"):
        if os.path.isfile(file) and (file.endswith(".csv") or file.endswith(".zip")):
            csv_files.append(file)

        if os.path.isfile(file) and file.endswith(".zip"):
            with zipfile.ZipFile(file, 'r') as zip:
                for zip_file in zip.namelist():
                    if zip_file.endswith(".csv"):
                        csv_files.append(f"{file}!{zip_file}")

    # Sort the list of CSV files by modification time, with newest first
    csv_files = sorted(csv_files, key=lambda f: get_modification_time(f), reverse=True)

    for i, file in enumerate(csv_files):
        print(f"{i + 1}: {file}")

    while True:
        try:
            choice = int(input("Enter the number of the file you want to choose: "))
            if choice < 1 or choice > len(csv_files):
                print("Invalid choice. Please enter a number from the list.")
            else:
                chosen_file = csv_files[choice - 1]
                break
        except ValueError:
            print("Invalid choice. Please enter a number from the list.")

    if chosen_file.endswith(".zip"):
        with zipfile.ZipFile(chosen_file, 'r') as zip:
            for zip_file in zip.namelist():
                if zip_file.endswith(".csv"):
                    with zip.open(zip_file, 'r') as csv_file:
                        temp_file = NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")
                        reader = csv.reader(io.StringIO(csv_file.read().decode()))
                        writer = csv.writer(temp_file)
                        for row in reader:
                            writer.writerow(row)
                        temp_file.close()
                        return temp_file.name
    else:
        with open(chosen_file, 'r') as csv_file:
            temp_file = NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")
            reader = csv.reader(csv_file)
            writer = csv.writer(temp_file)
            for row in reader:
                writer.writerow(row)
            temp_file.close()
            return temp_file.name

    return None

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




if __name__ == '__main__':
    choose_csv_file()
    