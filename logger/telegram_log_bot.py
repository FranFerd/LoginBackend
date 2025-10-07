import logging, aiohttp, asyncio
from configs.app_settings import settings

class TelegramHandler(logging.Handler):
    def __init__(self, bot_token: str, chat_id: str):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = settings.ERRORLOGGERULTRAPREMIUSBOT_BASE_URL
        self._loop = None

    def emit(self, record) -> None:
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)        
        
        # Schedule the async task
        if self._loop.is_running():
            # if loop is running, create task
            asyncio.create_task(self._async_emit(record))
        else:
            self._loop.run_until_complete(self._async_emit(record))

    async def _async_emit(self, record) -> None:
        log_entry = self.format(record)
        url = f"{self.base_url}{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": log_entry
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data) as response:
                    if response.status != 200:
                        print(f"Failed to send Telegram message: {response.status}")
        except Exception as e:
            print(f"Telegram handler error: {e}") # No 'raise' - logger shouldn't crash the application

class MarkdownFormatter(logging.Formatter):
    def format(self, record) -> str:
        # Format time first
        record.asctime = self.formatTime(record, self.datefmt)
        # Build markdown message
        msg = (
            f"*{record.levelname}* in `{record.module}` at `{record.asctime}`:\n"
            f"`{record.getMessage()}`"
        )
        return msg