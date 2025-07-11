from configs.database import Base, engine

async def create_tables() -> None:
    from models.user import UserModel # No need to use User. Importing is enough. 
                                 # Base.metadata.create_all() only creates tables for models that have already been imported into memory.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)