def validate_email_length(email: str) -> str:
    if len(email) > 254:
        raise ValueError("Email is 254 characters max")
    return email