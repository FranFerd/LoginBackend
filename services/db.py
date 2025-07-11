from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import or_
from models.user import UserModel
from schemas.user import UserCredentialsEmail
from security.password_hashing import Argon2Ph

class DbService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username_or_email(self, username: str, email: str):
        try:
            result = await self.db.execute(
                select(UserModel).where(
                    or_(
                        UserModel.username == username,
                        UserModel.email == email
                    )
                )
            )
            return result.scalars().all() # retuns a list of ORM objects
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while creating user"
            )
        
    async def insert_user(self, user: UserCredentialsEmail)-> UserModel:
        password_hashed = Argon2Ph().hash_password(user.password)
        new_user = UserModel(username=user.username, password_hashed=password_hashed, email=user.email)

        try:
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError as e:
            await self.db.rollback() # Always rollback on error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Username or email already exist: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error while creating user: {e}"
            )