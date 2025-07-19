import logging, requests
from configs.app_settings import settings

class TelegramHandler(logging.Handler):
    def __init__(self, bot_token: str, chat_id: str):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = settings.ERRORLOGGERULTRAPREMIUSBOT_BASE_URL

    def emit(self, record):
        log_entry = self.format(record)
        url = f"{self.base_url}{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": log_entry
        }
        try:
            requests.post(url, data=data)
        except Exception:
            raise

class MarkdownFormatter(logging.Formatter):
    def format(self, record):
        # Format time first
        record.asctime = self.formatTime(record, self.datefmt)
        # Build markdown message
        msg = (
            f"*{record.levelname}* in `{record.module}` at `{record.asctime}`:\n"
            f"`{record.getMessage()}`"
        )
        return msg