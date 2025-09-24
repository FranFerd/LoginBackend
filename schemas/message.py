from pydantic import BaseModel

class EmailConfirmMessage(BaseModel):
    message: str

class UserRegisteredMessage(BaseModel):
    message: str