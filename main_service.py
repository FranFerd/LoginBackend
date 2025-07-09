from fastapi import FastAPI
from contextlib import asynccontextmanager

class LoginMainService:
    def __init__(self):
        self.app = FastAPI(
            title="Login Project",
            description="Login Project is about signup, login, JWT",
            version="1.0.0"
        )

    def configure_cors(self):
        pass

    def configure_routers(self):
        pass

    def register_lifespan(self):
        pass

    def run(self):
        self.configure_cors()
        self.configure_routers()
        return self.app
