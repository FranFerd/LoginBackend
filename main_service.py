from fastapi import FastAPI
from contextlib import asynccontextmanager, _AsyncGeneratorContextManager

from configs.cors_config import add_cors_middleware
from configs.create_tables import create_tables

from logger.logger import logger

from routers.auth import router as auth_router
from routers.protected import router as protected_router
from routers.reset import router as reset_router

class LoginMainService:
    def _configure_lifespan(self) -> _AsyncGeneratorContextManager[None, None]:
        @asynccontextmanager # FastAPI expects lifespan to be async context manager. A context manager is an object you can use with 'async with' or 'with' that automatically handles setup and cleanup around a block of code.
        async def lifespan(app: FastAPI):
            logger.info("Server starting up...")
            await create_tables()

            try:
                yield
            finally:
                logger.info("Server shutting down...")
            
        return lifespan
        
    def __init__(self):
        self.lifespan = self._configure_lifespan()

        self.app = FastAPI(
            title="Login Project",
            description="Login Project is about signup, login, JWT",
            version="1.0.0",
            lifespan=self.lifespan
        )

    def _configure_cors(self) -> None:
        add_cors_middleware(self.app)

    def _configure_routers(self) -> None:
        self.app.include_router(auth_router)
        self.app.include_router(protected_router)
        self.app.include_router(reset_router)

    def run(self) -> FastAPI:
        self._configure_cors()
        self._configure_routers()
        return self.app
