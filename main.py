from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.db.database import engine, Base
from app.api.v1.endpoints import users, auth, polls

from app.core.exception import (
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    general_exception_handler
)
from app.core.constants import APIConfig

# Import models to register them with SQLAlchemy
from app.models import user, polls as poll_models

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Create FastAPI app with centralized configuration
app = FastAPI(
    title=APIConfig.API_TITLE,
    description=APIConfig.API_DESCRIPTION,
    version=APIConfig.API_VERSION
)

# Register exception handlers
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers with centralized prefix
app.include_router(users.router, prefix=APIConfig.API_V1_PREFIX)
app.include_router(auth.router, prefix=APIConfig.API_V1_PREFIX)
app.include_router(polls.router, prefix=APIConfig.API_V1_PREFIX)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Polls API!"}