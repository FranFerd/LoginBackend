from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import or_

from models.user import UserModel

from schemas.user import UserCredentialsEmail

from security.password_hashing import Argon2Ph

from typing import Optional
class DbService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username_or_email(
        self, 
        username: Optional[str] = None, 
        email: Optional[str] = None
    ) -> UserModel:
        if username is None and email is None:
            raise ValueError("At least one of 'username' or 'email' must be provided")
        
        try:
            conditions = []
            if username:
                conditions.append(UserModel.username == username) # Doesn't append True of False. SQLAlchemy overrides '==' to return an SQL expression 
            if email:
                conditions.append(UserModel.email == email)
            print(conditions)

            result = await self.db.execute(
                select(UserModel).where(or_(*conditions)) # or_ doesn't take list as argument. Unpack the list with unpacking operator *
            )
            return result.scalars().all() # retuns a list of ORM objects
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while fetching user"
            )
    
    async def get_username_by_email(self, email: str) -> str | None:
        try:
            result = await self.db.execute(
                select(UserModel.username).where(
                    UserModel.email == email
                )
            )
            return result.scalar_one_or_none()
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while fetching username"
            )
    async def insert_user(self, user: UserCredentialsEmail) -> UserModel:
        password_hashed = Argon2Ph().hash_password(user.password)
        new_user = UserModel(username=user.username, password_hashed=password_hashed, email=user.email)

        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db.rollback() # Always rollback on error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username or email already exist"
            )
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while creating user"
            )
        
    async def verify_user(self, username: str, password: str) -> bool:
        try:
            result = await self.db.execute(
                select(UserModel.password_hashed).where(UserModel.username == username)
            )
            hashed_password = result.scalar_one_or_none()

            if hashed_password is None:
                return False
            
            is_valid_password = Argon2Ph().verify_password(hashed_password, password)
            return is_valid_password
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while verifying user"
            )
    
    async def verify_email(self, email: str) -> bool:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            email = result.scalar_one_or_none()

            if email is None:
                return False
            
            return True
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while verifying email"
            )