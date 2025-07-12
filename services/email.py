import httpx
from configs.app_settings import settings
from schemas.email import EmailBody

class EmailService:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.MAILERSEND_API_KEY}",
            "Content-Type": "application/json" 
        }

    async def send_email(self, email_body: EmailBody):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.MAILERSEND_BASE_URL, 
                json=email_body.model_dump(by_alias=True), # Pydantic method that converts model into a dict, fields use aliases.
                headers=self.headers                       # Can't send Pydantic models where JSON is required. model_dump converts to dict, which is JSON-serializable
            )
            response.raise_for_status()
            return response.json() # json() is httpx method that converts JSON into Python object