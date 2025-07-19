import yagmail
from configs.app_settings import settings
from utils.email_contents import email_contents
from logger.logger import logger

class EmailService:
    def __init__(self):
        self.yag = yagmail.SMTP(settings.YAGMAIL_MY_EMAIL)

    def _send_email(self, to: str, subject: str, contents: str) -> None: # Turn VPN off before sending
        try:
            self.yag.send(
                to=to,
                subject=subject,
                contents=contents
            )
        except Exception as e:
            logger.exception("Unexpected error while sending email")
            raise e

    def send_password_reset_email(self, email: str, username: str, token: str) -> None:
        text_fallback = email_contents.get_plain_text_password_reset(username, token)
        html_content = email_contents.get_html_password_reset(username, token)
        self._send_email(
            email,
            subject="Password reset",
            contents=[text_fallback, html_content]
        )

    def send_email_confirm(self, email: str, username: str) -> None: # Add hello, username
        text_fallback = email_contents.get_plain_text_email_confirm(username)
        html_content = email_contents.get_html_email_confirm(username)
        self._send_email(
            email,
            subject="Email confirmation",
            contents=[text_fallback, html_content]
        )
        
email_service = EmailService()