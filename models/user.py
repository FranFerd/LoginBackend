from sqlalchemy import Column, Integer, String, DateTime, func
from configs.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(12), nullable=False, unique=True) #unique also creates a regular index to improve query speed(index=True)
    password_hashed = Column(String(255), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    #server_default=func.now()... tells DB to fill the value using NOW(). More reliable than python (run at the moment of insertion, not before)