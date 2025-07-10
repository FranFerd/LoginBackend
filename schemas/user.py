from pydantic import BaseModel
from datetime import timedelta

class User(BaseModel):
    id: int
    username: str
    password_hashed: str
    email: str
    created_at: timedelta