from fastapi import FastAPI
from contextlib import asynccontextmanager
from configs.cors_config import add_cors_middleware
from database import create_table

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
        pass

    def configure_lifespan(self):
        @asynccontextmanager # FastAPI expects lifespan to be async context manager. A context manager is an object you can use with 'async with' or 'with' that automatically handles setup and cleanup around a block of code.
        async def lifespan(app: FastAPI): # Handles 
            print("App is running...")
            await create_table()
            yield
            print("App is shutting down...")

        self.app.router.lifespan_context = lifespan # No need to call

    def run(self):
        self.configure_cors()
        self.configure_routers()
        self.configure_lifespan()
        return self.app
