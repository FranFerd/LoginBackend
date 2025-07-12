from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenSub(BaseModel):
    username: str