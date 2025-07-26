from logger.logger import logger

import yagmail

from configs.app_settings import settings

from utils.email_contents import EmailContents

from schemas.exceptions import EmailSendError

class EmailService:
    def __init__(self):
        self.yag = yagmail.SMTP(settings.YAGMAIL_MY_EMAIL)

    def _send_email(
        self, 
        to: str, 
        subject: str, 
        contents: str
    ) -> None: # Turn VPN off before sending
        
        try:
            self.yag.send(
                to=to,
                subject=subject,
                contents=contents
            )

        except Exception as e:
            logger.exception("Unexpected error while sending email")
            raise EmailSendError from e

    def send_password_reset_email(
        self, 
        email: str, 
        username: str, 
        token: str
    ) -> None:
        
        text_fallback = EmailContents.get_plain_text_password_reset(username, token)
        html_content = EmailContents.get_html_password_reset(username, token)
        self._send_email(
            email,
            subject="Password reset",
            contents=[text_fallback, html_content]
        )
        logger.info(f"Password reset link sent to {email}")

    def send_email_confirm(
        self, 
        email: str, 
        username: str,
        code: str
    ) -> None:
        
        text_fallback = EmailContents.get_plain_text_email_confirm(username, code)
        html_content = EmailContents.get_html_email_confirm(username, code)
        self._send_email(
            email,
            subject="Email confirmation",
            contents=[text_fallback, html_content]
        )
        logger.info(f"Email confirmation code sent to {email}")
        
email_service = EmailService()