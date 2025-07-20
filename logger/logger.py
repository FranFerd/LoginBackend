import logging, os
from pythonjsonlogger import jsonlogger
from logger.telegram_log_bot import TelegramHandler, MarkdownFormatter
from configs.app_settings import settings

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Sets the minimum severity level of log messages this logger will process. DEBUG is the lowest level

formatter = jsonlogger.JsonFormatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(filename=f"{LOG_DIR}/app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

telegram_handler = TelegramHandler(
    bot_token=settings.ERRORLOGGERULTRAPREMIUSBOT_TOKEN,
    chat_id=settings.ERRORLOGGERULTRAPREMIUSBOT_CHAT_ID
)
telegram_handler.setLevel(logging.ERROR)
telegram_handler.setFormatter(MarkdownFormatter())

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(telegram_handler)