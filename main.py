from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging import configure_logging
from core.database import engine, Base
from core import models
from features.auth.routes import auth_router
from core.utils.exception_handler import AppException, app_exception_handler

configure_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True)

app.include_router(auth_router)
