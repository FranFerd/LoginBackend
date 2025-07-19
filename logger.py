import logging
from pythonjsonlogger import jsonlogger
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Sets the minimum severity level of log messages this logger will process. DEBUG is the lowest level

formatter = jsonlogger.JsonFormatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(filename=f"{LOG_DIR}/app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)


if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)