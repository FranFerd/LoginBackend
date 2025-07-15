from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError

from configs.app_settings import settings

from schemas.token import TokenSub, TokenResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token') # extracts JWT from authorization header
def decode_token(
    token: str = Depends(oauth2_scheme)
) -> TokenSub:
    try:
        payload: dict = jwt.decode(token, settings.JWT_SECRET, settings.ALGORITHM) # returns whatever is jwt.encode
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return TokenSub(username=username) # takes only positional arguments
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
def get_token_from_header(token: str = Depends(oauth2_scheme)) -> TokenResponse:
    return TokenResponse( # Depends raises an error itself if no token
        access_token=token,
        token_type='bearer'
    )