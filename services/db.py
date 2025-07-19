from logger import logger

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import or_, update

from models.user import UserModel

from schemas.user import UserCredentialsEmail

from security.password_hashing import Argon2Ph

from typing import Optional, List

class DbService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username_or_email(
        self, 
        username: Optional[str] = None, 
        email: Optional[str] = None
    ) -> List[UserModel]:
        
        if username is None and email is None:
            logger.warning("Username or email not provided")
            raise ValueError("At least one of 'username' or 'email' must be provided")
        
        try:
            conditions = []
            if username:
                conditions.append(UserModel.username == username) # Doesn't append True of False. SQLAlchemy overrides '==' to return an SQL expression 
            if email:
                conditions.append(UserModel.email == email)

            result = await self.db.execute(
                select(UserModel).where(or_(*conditions)) # or_ doesn't take list as argument. Unpack the list with unpacking operator *
            )
            return result.scalars().all() # Returns a list of ORM objects 
        except Exception:
            await self.db.rollback()
            logger.exception("Unexpected error while fetching user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while fetching user"
            )
        
    async def insert_user(
        self, 
        user: UserCredentialsEmail
    ) -> UserModel:
        
        password_hashed = Argon2Ph().hash_password(user.password)
        new_user = UserModel(username=user.username, password_hashed=password_hashed, email=user.email)

        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db.rollback() # Always rollback on error
            logger.exception(f"IntegrityError while inserting user: username={user.username}, email={user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username or email already exist"
            )
        except Exception:
            await self.db.rollback()
            logger.exception("Unexpected error while creating user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while creating user"
            )
        
    async def verify_user(
        self, 
        username: str, 
        password: str
    ) -> bool:
        
        try:
            result = await self.db.execute(
                select(UserModel.password_hashed).where(UserModel.username == username)
            )
            hashed_password = result.scalar_one_or_none()

            if hashed_password is None:
                logger.warning(f"Login failed: user not found or password incorrect for '{username}'") # Add {username}?
                return False
            
            is_valid_password = Argon2Ph().verify_password(hashed_password, password)
            return is_valid_password
        except Exception:
            logger.exception("Unexpected error while verifying user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while verifying user"
            )
    
    async def verify_email(
        self, 
        email: str
    ) -> bool:
        
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()

            if user is None:
                logger.warning(f"No user found with email '{email}'")
                return False
            
            return True
        except Exception:
            logger.exception("Unexpected error while verifying email")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while verifying email"
            )
        
    async def update_password(
        self, 
        username: str, 
        new_password: str
    ) -> None:
        new_password_hashed = Argon2Ph().hash_password(new_password)

        try:
            statement = (
                update(UserModel)
                .where(UserModel.username == username)
                .values(password_hashed=new_password_hashed)
            )
            result = await self.db.execute(statement)

            if result.rowcount == 0:
                logger.warning(f"User '{username}' not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="User not found"
                )
            
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            logger.exception("Unexpected error while updating user")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while updating user"
            )