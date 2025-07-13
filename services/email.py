import yagmail
from configs.app_settings import settings

class EmailService:
    def __init__(self):
        self.yag = yagmail.SMTP(settings.YAGMAIL_MY_EMAIL)
    
    def send_password_reset_email(self, email: str) -> None: # Turn VPN off before sending email
        try:
            self.yag.send(
                to=email,
                subject="Password reset",
                contents="Here's the link to reset your password",
            )
        except Exception as e:
            raise e

email_service = EmailService()