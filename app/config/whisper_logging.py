import logging
import os
from datetime import datetime

# Define the base upload directory
logging_upload_directory = os.path.join("logs")

# Generate a log file name based on the current date and time
log_filename = datetime.now().strftime("app_%Y-%m-%d.log")

# Ensure the upload directory exists
os.makedirs(logging_upload_directory, exist_ok=True)

# Create a custom logger
logger = logging.getLogger("whisper_module")

# Set the global logging level
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(os.path.join(logging_upload_directory, log_filename))

# Set the logging level for handlers
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.ERROR)

# Create formatters and add them to handlers
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console_handler.setFormatter(console_formatter)
file_handler.setFormatter(file_formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def write_log_debug(message: str):
    logger.debug(message)


def write_log_info(message: str):
    logger.info(message)
    print(message)


def write_log_warning(message: str):
    logger.warning(message)


def write_log_error(message: str):
    logger.error(message)
    print(message)


def write_log_critical(message: str):
    logger.critical(message)
