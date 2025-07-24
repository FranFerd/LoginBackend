from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from datetime import datetime

from utils.email_validator import validate_email_length

class UserSchema(BaseModel):
    id: int
    username: str
    password_hashed: str
    email: str
    created_at: datetime

    model_config = {
        "from_attributes": True # Now Pydantic can read attributes from ORM objects (not just dicts)
    }                           # It is Needed to pass models with model_validate(orm_obj)

class Credentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=12) # '...' is required to make it not optional when using Field. Without Field, fields are required by default
    password: str = Field(..., min_length=6, max_length=30)
    email: EmailStr

    @field_validator('email')
    @classmethod # Needed for Pydantic firld validation
    def check_email_length(cls, v):
        return validate_email_length(v)

class CredentialsHashed(BaseModel):
    username: str = Field(..., min_length=3, max_length=12) # '...' is required to make it not optional when using Field. Without Field, fields are required by default
    hashed_password: str = Field(..., min_length=6, max_length=255)
    email: EmailStr

    @field_validator('email')
    @classmethod # Needed for Pydantic firld validation
    def check_email_length(cls, v):
        return validate_email_length(v)
    
class UsernameEmail(BaseModel):
    username: str
    email: str

class Email(BaseModel):
    address: EmailStr

    @field_validator('address')
    @classmethod # Needed for Pydantic firld validation
    def check_email_length(cls, v):
        return validate_email_length(v)

class PasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=30)
    new_password_confirm: str = Field(..., min_length=6, max_length=30)
    
    @model_validator(mode='after') # 'after': run check_passwords after all fields have been validated by Pydantic (e.g. is this a str, its min and max length, etc)
    def check_passwords_match(self) -> "PasswordResetRequest": 
        if self.new_password != self.new_password_confirm:
            raise ValueError("Passwords do not match")
        return self # Always return self after validation. If not - error
    
class CodeAndEmail(BaseModel):
    code: str
    email: str