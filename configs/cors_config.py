from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.app_settings import settings

def add_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True, # Allow browser to send and receive credentials (cookies, authorization headers)
        allow_methods=["*"], # Allow all HTTP requests
        allow_headers=["*"]  # Allow all headers (Authorization)
    )