from fastapi import FastAPI
from contextlib import asynccontextmanager
from configs.cors_config import add_cors_middleware
from configs.create_tables import create_tables

from routers.auth import router as auth_router
from routers.protected import router as protected_router
from routers.reset import router as reset_router

class LoginMainService:
    def __init__(self):
        self.app = FastAPI(
            title="Login Project",
            description="Login Project is about signup, login, JWT",
            version="1.0.0"
        )

    def configure_cors(self):
        add_cors_middleware(self.app)

    def configure_routers(self):
        self.app.include_router(auth_router)
        self.app.include_router(protected_router)
        self.app.include_router(reset_router)

    def configure_lifespan(self):
        @asynccontextmanager # FastAPI expects lifespan to be async context manager. A context manager is an object you can use with 'async with' or 'with' that automatically handles setup and cleanup around a block of code.
        async def lifespan(app: FastAPI): # Handles 
            print("App is running...")
            await create_tables()
            yield
            print("App is shutting down...")

        self.app.router.lifespan_context = lifespan # No need to call

    def run(self):
        self.configure_cors()
        self.configure_routers()
        self.configure_lifespan()
        return self.app
