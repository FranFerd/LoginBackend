class EmailContents:

    @staticmethod
    def get_html_email_confirm(username: str, code: str) -> str:
        return f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <h2 style="color: #4A90E2;">Email Verification Code</h2>
                <h3>Hello, {username}</h3>
                <h4>Use the following <strong>verification code</strong> to complete your sign-up:</h4>
                <h1>{code}</h1>
                <h4>This code will expire in 30 minutes.</h4>
                <h4>Yours truly,<br>Login Project</h4>
            </body>
            </html>
            """
    
    @staticmethod
    def get_plain_text_email_confirm(username: str, code: str) -> str:
        return f"Hi, {username}. Your verification code is {code}. Yours truly, Login Project"
    
    @staticmethod
    def get_html_password_reset(username: str, token: str) -> str:
        link = f"http://localhost:3000//password-reset?token={token}"
        return f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <h2 style="color: #4A90E2;">Password reset</h2>
                <h3>Hello, {username}</h3>
                <h4>Use the following <strong>link</strong> to reset your password:</h4>
                <a href={link}>{link}<a>
                <h4>The link will become invalid in 10 minutes</h4>
                <h4>Yours truly,<br>Login Project</h4>
            </body>
            </html>
            """  
          
    @staticmethod
    def get_plain_text_password_reset(username: str, token: str) -> str:
        link = f"http://localhost:3000//password-reset?token={token}"
        return f"Hi, {username}. The link to reset your password: {link}. Yours truly, Login Project"