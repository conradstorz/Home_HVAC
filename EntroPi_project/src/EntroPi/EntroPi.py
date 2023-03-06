"""A self contained and systemd service enabled package for monitoring temperatures"""
__version__ = "0.2.1"

# These imports and constants are used by Loguru
from CONSTANTS import TIME_NOW
from pathlib import Path
from loguru import logger
RUNTIME_NAME = Path(__file__).name
RUNTIME_CWD = Path.cwd()
OS_FILENAME_SAFE_TIMESTR = "".join(i for i in TIME_NOW if i not in "\/:*?<>|")
import datetime as dt
import os


from humidity_and_temps_recorder import main
# This file is a wrapper around temperature monitor program.


@logger.catch
def defineLoggers(filename):
    """Standardize the logging setup here.
    """
    # Begin logging definition
    logger.remove()  # removes the default console logger provided by Loguru.
    # I find it to be too noisy with details more appropriate for file logging.

    # if using the tqdm module .write method to allow tqdm to display correctly.
    # logger.add(lambda msg: tqdm.write(msg, end=""), format="{message}", level="ERROR")

    logger.configure(handlers=[{"sink": os.sys.stderr, "level": "INFO"}])
    # this method automatically suppresses the default handler to modify the message level

    # here is the actual file logger definition. It rotates the logs at noon, specifies "DEBUG" and above and compresses old logs.
    logger.add(
        "".join(["./LOGS/", filename, "_{time}.log"]),
        rotation="12:00",
        level="DEBUG",
        encoding="utf8",
        compression="zip",
    )
    
    return


defineLoggers(f"{RUNTIME_NAME}_{OS_FILENAME_SAFE_TIMESTR}")
logger.info("Program Start.")  # log the start of the program
main()
logger.info("Program End.")
