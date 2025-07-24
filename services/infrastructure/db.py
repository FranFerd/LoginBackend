from logger.logger import logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy import or_, update

from models.user import UserModel

from schemas.user import CredentialsHashed
from schemas.exceptions import DatabaseError, UserAlreadyExistsError, UserNotFound

from security.password_hashing import argon2_ph

from typing import Optional, List

class DbService:
    def __init__(self, db: AsyncSession):

        try:
            self.db = db
            logger.info("DB service initialized successfully")

        except Exception:
            logger.critical("Failed to initialize DB service")
            raise # 'raise' is better that 'raise e' because traceback starts where the error happened, not where it was caught (raise e)

    async def get_user_by_username_or_email(
        self, 
        username: Optional[str] = None, 
        email: Optional[str] = None
    ) -> List[UserModel]:
        
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
        
        except Exception as e:
            await self.db.rollback()
            logger.exception("Unexpected error while fetching user")
            raise DatabaseError("Failed to get user") from e
        
    async def insert_user(
        self, 
        credentials_hashed: CredentialsHashed
    ) -> UserModel:
        
        new_user = UserModel(
            username=credentials_hashed.username, 
            password_hashed=credentials_hashed.hashed_password, 
            email=credentials_hashed.email
        )

        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user) # after adding and commit, new_user may not have all fields populated (auto-generated id, default values Timestamp)
            return new_user
        
        except IntegrityError as e: # Occurs when constraints are violated (unique, not null, fks)
            await self.db.rollback() # Always rollback on error
            logger.info(f"IntegrityError while inserting user: username={credentials_hashed.username}, email={credentials_hashed.email}")
            raise UserAlreadyExistsError("Username or email already in use") from e
        
        except Exception as e:
            await self.db.rollback()
            logger.exception("Unexpected error while creating user")
            raise DatabaseError("Unexpected database error during user insert") from e
        
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
                logger.info(f"Login failed: user not found or password incorrect for '{username}'")
                return False
            
            is_valid_password = argon2_ph.verify_password(hashed_password, password)
            return is_valid_password
        
        except Exception as e:
            logger.exception("Unexpected error while verifying user")
            raise DatabaseError("Unexpected database error during user verification") from e
        
    async def update_password(
        self, 
        username: str, 
        new_password: str
    ) -> None:
        new_password_hashed = argon2_ph.hash_password(new_password)

        try:
            statement = (
                update(UserModel)
                .where(UserModel.username == username)
                .values(password_hashed=new_password_hashed)
            )
            result = await self.db.execute(statement)

            if result.rowcount == 0:
                logger.info(f"User '{username}' not found in DB during password update")
                raise UserNotFound(f"User '{username} not found'")
            
            await self.db.commit()
            logger.info(f"Password updated for user '{username}'")

        except Exception as e:
            await self.db.rollback()
            logger.exception("Unexpected error while updating user")
            raise DatabaseError("Unexpected database error during password update") from e