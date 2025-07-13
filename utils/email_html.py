import random
def get_html_email_confirm() -> str:
    i = 0
    code = []
    while i < 6: 
        code.append(random.randint(0, 9))
        i += 1
    print(code)
    return f"""
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

get_html_email_confirm()