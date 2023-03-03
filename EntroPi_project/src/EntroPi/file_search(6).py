"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""

from tempfile import NamedTemporaryFile
from zipfile import ZipFile
import os

def extract_csv_file(file_path):
    csv_files = []
    for file in os.listdir("."):
        if file.endswith(".csv"):
            csv_files.append(file)
        elif file.endswith(".zip"):
            with ZipFile(file, 'r') as zip:
                for zip_file in zip.namelist():
                    if zip_file.endswith(".csv"):
                        csv_files.append(f"{file}!{zip_file}")
    
    if len(csv_files) == 0:
        print("No CSV files found.")
        return None
    
    csv_files = sorted(csv_files, key=lambda f: get_modified_time(f), reverse=True)
    
    for i, file in enumerate(csv_files):
        print(f"{i+1}. {file}")
    
    while True:
        choice = input(f"Enter the number of the CSV file to extract (1-{len(csv_files)}) or 'q' to quit: ")
        if choice.lower() == 'q':
            return None
        
        try:
            choice = int(choice)
            if choice < 1 or choice > len(csv_files):
                raise ValueError
        except ValueError:
            print("Invalid input. Please enter a valid number or 'q' to quit.")
            continue
        
        file = csv_files[choice-1]
        if "!" in file:
            with ZipFile(file.split("!")[0], 'r') as zip:
                with zip.open(file.split("!")[1], 'r') as csv:
                    temp_file = NamedTemporaryFile(mode='w+t', delete=False, suffix='.csv')
                    temp_file.write(csv.read().decode())
        else:
            with open(file, 'r') as csv:
                temp_file = NamedTemporaryFile(mode='w+t', delete=False, suffix='.csv')
                temp_file.write(csv.read())
        
        temp_file.close()
        return temp_file.name

def get_modified_time(file_path):
    if "!" in file_path:
        zip_path, inner_path = file_path.split("!")
        with ZipFile(zip_path, 'r') as zip:
            return max(zip.getinfo(inner_path).date_time)
    else:
        return os.path.getmtime(file_path)
