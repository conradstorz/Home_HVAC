from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def zip_files(filePath, remove_uncompressed_file=False):
    # Initialize the ZIP file
    # TODO verify file exists and is non-zero sized
    zipfilepath = filePath.with_suffix(".zip")
    with ZipFile(zipfilepath, "w") as target:
        # Add the file to the ZIP file
        target.write(file_path, compress_type=ZIP_DEFLATED)
        print(
            f"{file_path} file has been compressed into {zipfilepath}"
        )  # TODO add details
    if remove_uncompressed_file:
        # TODO implement removal of uncompressed file
        # verify zip exists
        # verify zip has no errors
        # verify zip contains target file
        # verify target file is a file
        # verify target file is non-zero sized
        # unlink file to remove
        # verify file no longer exists
        pass
    return


directory = "./"
# Search for CSV files in the directory
for file_path in Path(directory).glob("*.csv"):
    # TODO sort out active files (e.g. todays file) and only compress older files
    zip_files(file_path)
    # TODO verify file was placed inside of a zip file and delete original
    # should likely be part of the zip_files function

"""
from pathlib import Path
from datetime import datetime, date

def get_files_before_today(directory):
    today = date.today()
    files_before_today = []
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            try:
                file_date = datetime.strptime(file_path.stem.split("_")[0], '%Y-%m-%d')
                if file_date.date() < today:
                    files_before_today.append(file_path)
            except ValueError:
                pass
    return files_before_today

# Example usage
directory = 'path/to/directory'
files_before_today = get_files_before_today(directory)
for file in files_before_today:
    print(file)

"""
