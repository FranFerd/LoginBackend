from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserSchema(BaseModel):
    id: int
    username: str
    password_hashed: str
    email: str
    created_at: datetime

    model_config = {
        "from_attributes": True # Now Pydantic can read attributes from ORM objects (not just dicts)
    }                           # It is Needed to pass models with model_validate(orm_obj)

class UserCredentialsEmail(BaseModel):
    username: str = Field(max_length=12)
    password: str = Field(max_length=30)
    email: EmailStr = Field(max_length=254)
