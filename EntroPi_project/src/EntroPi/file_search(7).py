"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""

import os
import zipfile
from tempfile import NamedTemporaryFile
from glob import glob

def choose_file():
    csv_files = []
    for file in glob("*"):
        if file.endswith(".csv"):
            csv_files.append(file)
        elif file.endswith(".zip"):
            with zipfile.ZipFile(file, 'r') as zip:
                for zip_file in zip.namelist():
                    if zip_file.endswith(".csv"):
                        csv_files.append(f"{file}!{zip_file}")

    if not csv_files:
        print("No CSV files found.")
        return None

    csv_files = sorted(csv_files, key=lambda f: os.path.getmtime(f), reverse=True)

    for i, file in enumerate(csv_files):
        print(f"{i + 1}: {file}")

    while True:
        try:
            choice = int(input("Select a file number to process: "))
            if choice < 1 or choice > len(csv_files):
                print("Invalid choice. Please enter a valid file number.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid file number.")

    file_choice = csv_files[choice - 1]

    if "!" in file_choice:
        zip_file, csv_file = file_choice.split("!")
        with zipfile.ZipFile(zip_file, 'r') as zip:
            with zip.open(csv_file) as csv:
                temp_file = NamedTemporaryFile(mode="w", delete=False, suffix=".csv")
                temp_file.write(csv.read().decode())
                temp_file.close()
                return temp_file.name
    else:
        temp_file = NamedTemporaryFile(mode="w", delete=False, suffix=".csv")
        with open(file_choice) as csv:
            temp_file.write(csv.read())
        temp_file.close()
        return temp_file.name
