"""revised ChatGPT generated code to find files and display a list for selection of a particular file by the user.

    This code searches inside of zipfiles and finds matches there as well.
    Results are shown sorted newest to oldest file.
"""
import glob
import os
import zipfile
import io
from tempfile import NamedTemporaryFile
from datetime import datetime
from loguru import logger


@logger.catch
def main():
    # Get a list of all CSV files in the current directory and its subdirectories, while ignoring certain directories
    ignore_dirs = ["venv", "dist"]
    csv_files = []
    for file in glob.iglob('**/*.csv', recursive=True):
        if not any(d in file for d in ignore_dirs):
            csv_files.append(file)

    # Get a list of all ZIP files in the current directory and its subdirectories, while ignoring certain directories
    zip_files = []
    for file in glob.iglob('**/*.zip', recursive=True):
        if not any(d in file for d in ignore_dirs):
            # logger.debug(f'Including file: {file}')
            zip_files.append(file)
        else:
            logger.debug(f'Excluding file: {file}')

    # Combine the lists of CSV and ZIP files
    files = csv_files + zip_files
    # logger.debug(f'\n{files=}\n')
    # Sort the list of files by modification time (newest first)
    files = sorted(files, key=lambda f: os.path.getmtime(f), reverse=True)
    # logger.debug(f'\n{files=}\n')

    # Ask the user to choose a file
    while True:
        print("Available CSV files:")
        for i, file in enumerate(files):
            print(f"{i+1}. {os.path.basename(file)}")

        choice = input("Enter the number of the CSV file to plot (or q to quit): ")
        if choice.lower() == "q":
            exit()
        try:
            choice = int(choice)
            if 1 <= choice <= len(files):
                break
        except ValueError:
            pass
        print('Invalid choice. Please try again.')

    # Determine if the chosen file is a CSV or a ZIP file
    file = files[choice - 1]
    if file.endswith('.csv'):
        # If the chosen file is a CSV, open it directly as a file object
        with open(file, 'r') as csv_file:
            # Read the CSV data and write it to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(csv_file.read())

        print(f'The chosen file "{os.path.basename(file)}" has been extracted to {temp_file.name}.')
    else:
        # If the chosen file is a ZIP, extract the CSV file to a temporary file
        with zipfile.ZipFile(file, 'r') as zip_file:
            csv_file = None
            for name in zip_file.namelist():
                if name.endswith('.csv'):
                    csv_file = name
                    break
            if csv_file is not None:
                with zip_file.open(csv_file, 'r') as csv:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                        temp_file.write(io.StringIO(csv.read().decode()).getvalue())

                print(f'The chosen file "{os.path.basename(file)}:{csv_file}" has been extracted to {temp_file.name}.')
            else:
                print(f'The chosen file "{os.path.basename(file)}" does not contain a CSV file.')

if __name__ == '__main__':
    main()
