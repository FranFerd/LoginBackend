from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from configs.app_settings import settings

engine = create_async_engine(url=settings.DATABASE_URL, echo=True) # 'echo=True' logs SQL queries to console

async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

# if expire_on_commit=True, after commit, when I print(user.username), SQLAlchemy will try to refetch user.username from DB, but the session closes after commit -> error
# if expire_on_commit=False, SQLAlchemy uses whatever is currently in memory, which may be stale. Only a problem when strong consistency is needed (banking) 