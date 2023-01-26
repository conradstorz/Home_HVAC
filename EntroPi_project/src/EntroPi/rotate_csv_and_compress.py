from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from loguru import logger
from datetime import datetime
from CONSTANTS import *


def generate_csv_filename(basename = None):
    if basename == None:
        basename = BASENAME_CSV_FILE
    return f'{datetime.now().strftime("%Y%m%d")}{basename}.csv'

@logger.catch
def zip_files(uncompressed_file_path, remove_uncompressed_file=False):
    # Initialize the ZIP file
    # TODO verify file exists and is non-zero sized
    zipfile_path = uncompressed_file_path.with_suffix(".zip")
    with ZipFile(zipfile_path, "w") as target:
        # Add the file to the ZIP file
        target.write(uncompressed_file_path, compress_type=ZIP_DEFLATED)
        print(
            f"{uncompressed_file_path} file has been compressed into {zipfile_path}"
        )  # TODO add details
        if remove_uncompressed_file:
            # TODO implement removal of uncompressed file
            if zipfile_path.exists(): # verify zip exists
                print('zip file exists')
                if target.testzip() == None: # verify zip contains no invalid files
                    print('zip file is valid')
                    print(target.namelist())
                    if uncompressed_file_path.name in target.namelist(): # verify zip contains target file
                        print('is inside zipfile')
                        if uncompressed_file_path.is_file(): # verify target file is a file
                            print('is file')
                            if uncompressed_file_path.stat().st_size > 0: # verify target file is non-zero sized
                                print('is non-zero')
                                uncompressed_file_path.unlink()  # unlink file to remove
                            else:
                                # TODO log inability to remove file
                                print(f'Unable to remove un-compressed file: {uncompressed_file_path}')
            if uncompressed_file_path.exists(): # verify file no longer exists
                # TODO log file exists when it shouldn't
                print(f'File removal failed: {uncompressed_file_path}')
            else:
                # TODO log success
                print(f'File "{uncompressed_file_path}" sucessfully removed.')
        else:
            print(f'Un-compressed file not removed per design.')
    return


@logger.catch
def compress_local_csv(directory = None):
    print('Start compress function.')
    if directory == None:
        directory = "./"
    # Search for CSV files in the directory
    active_recorder_file = generate_csv_filename(basename=BASENAME_CSV_FILE)
    # csv_files_in_local_directory = Path(directory).glob("*.csv")
    csv_files_found = list(Path(directory).glob("*.csv"))
    print(f'files found: {csv_files_found}')
    print(f'Length of list: {len(csv_files_found)}')
    if len(csv_files_found) > 1:
        print('loop over files')
        for file_path in csv_files_found:
            print(f'file: {file_path.name}')
            # TODO sort out active files (e.g. yesterday and todays file) and only compress older files
            print(f'{file_path.name} *** {active_recorder_file}')
            if file_path.name != active_recorder_file:
                zip_files(file_path, remove_uncompressed_file=True)
            else:
                print(f'Skipping: {active_recorder_file} as per design.')


if __name__ == "__main__":
    compress_local_csv()


"""
from pathlib import Path
from datetime import datetime, date

def get_files_before_today(directory):
    today = date.today()
    yesterday = today - 1
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
