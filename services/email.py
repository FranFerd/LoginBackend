import yagmail
from configs.app_settings import settings

class EmailService:
    def __init__(self):
        self.yag = yagmail.SMTP(settings.YAGMAIL_MY_EMAIL)

    def _send_email(self, to: str, subject: str, contents: str) -> None:
        try:
            self.yag.send(
                to=to,
                subject=subject,
                contents=contents
            )
        except Exception as e:
            raise e

    def send_password_reset_email(self, email: str) -> None: # Turn VPN off before sending email
        self._send_email(
            email,
            subject="Password reset",
            contents="Here's the link to reset your password"
        )

    def send_email_confirm(self, email: str) -> None: # Add hello, username
        code = "123456"
        html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <h2 style="color: #4A90E2;">Email Verification Code</h2>
                <h3>Hello, </h3>
                <h4>Use the following <strong>verification code</strong> to complete your sign-up:</h4>
                <h1>{code}</h1>
                <h4>This code will expire in 10 minutes.</h4>
                <h4>Thanks,<br>Login Project</h4>
            </body>
            </html>
            """

        self.yag.send(
            email,
            subject="Email confirmation",
            contents=html_content
        )
        
email_service = EmailService()