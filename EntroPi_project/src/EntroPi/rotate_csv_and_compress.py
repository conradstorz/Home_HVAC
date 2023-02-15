from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from loguru import logger
from datetime import datetime
from CONSTANTS import *


@logger.catch
def generate_csv_filename(basename=None):
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
        logger.info(
            f"{uncompressed_file_path} file has been compressed into {zipfile_path}"
        )  # TODO add details
        if remove_uncompressed_file:
            # TODO implement removal of uncompressed file
            if zipfile_path.exists():  # verify zip exists
                logger.info("zip file exists")
                if target.testzip() == None:  # verify zip contains no invalid files
                    logger.info("zip file is valid")
                    logger.info(target.namelist())
                    if (
                        uncompressed_file_path.name in target.namelist()
                    ):  # verify zip contains target file
                        logger.info("is inside zipfile")
                        if (
                            uncompressed_file_path.is_file()
                        ):  # verify target file is a file
                            logger.info("is file")
                            if (
                                uncompressed_file_path.stat().st_size > 0
                            ):  # verify target file is non-zero sized
                                logger.info("is non-zero")
                                uncompressed_file_path.unlink()  # unlink file to remove
                            else:
                                # TODO log inability to remove file
                                logger.info(
                                    f"Unable to remove un-compressed file: {uncompressed_file_path}"
                                )
            if uncompressed_file_path.exists():  # verify file no longer exists
                # TODO log file exists when it shouldn't
                logger.info(f"File removal failed: {uncompressed_file_path}")
            else:
                # TODO log success
                logger.info(f'File "{uncompressed_file_path}" sucessfully removed.')
        else:
            logger.debug(f"Un-compressed file '{uncompressed_file_path.name}' not removed per design.")
            pass
    return


@logger.catch
def compress_local_csv(directory=None):
    logger.debug("Start compress function.")
    if directory == None:
        directory = "./"
    # Search for CSV files in the directory
    active_recorder_file = generate_csv_filename(basename=BASENAME_CSV_FILE)
    # csv_files_in_local_directory = Path(directory).glob("*.csv")
    csv_files_found = list(Path(directory).glob("*.csv"))
    logger.debug(f"files found matching compression filter: {csv_files_found}")
    logger.debug(f"Length of list: {len(csv_files_found)}")
    if len(csv_files_found) >= 1:
        logger.debug("loop over files")
        for file_path in csv_files_found:
            logger.debug(f"file: {file_path.name}")
            # TODO sort out active files (e.g. yesterday and todays file) and only compress older files
            logger.debug(f"{file_path.name} *** {active_recorder_file}")
            if file_path.name != active_recorder_file:
                zip_files(file_path, remove_uncompressed_file=True)
            else:
                logger.debug(f"Skipping: {active_recorder_file} as per design.")
                pass


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
    logger.info(file)

"""
