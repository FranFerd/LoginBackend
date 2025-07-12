from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class Email(BaseModel):
    email: EmailStr

class EmailAddress(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class EmailBody(BaseModel): # Field is used to add constraints, aliases, min/max length, default.
    from_: EmailAddress = Field(..., alias='from') # from is python-reserved keyword. '...' means the value is required, without it, the field is optional
    to: List[EmailAddress]
    subject: str
    html: str