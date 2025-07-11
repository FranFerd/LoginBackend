from fastapi import HTTPException, status
from services.db import DbService
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCredentialsEmail, UserSchema

class UserService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def signup(self, user_credentials_email: UserCredentialsEmail)-> UserSchema:
        # With Pydantic Models there's no need to validate if Models exist (e.g if user_credentials_email), Pydantic does it automatically

        existing_users = await self.db_service.get_user_by_username_or_email(
            user_credentials_email.username, 
            user_credentials_email.email)
        
        if not existing_users:
            new_user = await self.db_service.insert_user(user_credentials_email)
            return UserSchema.model_validate(new_user)

        if len(existing_users) == 2:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username and email already in use"
                )
        
        user = existing_users[0] 
        if user.username == user_credentials_email.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username already exists")
        if user.email == user_credentials_email.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
            
            