from pydantic import BaseModel

class EmailConfirmMessage(BaseModel):
    message: str