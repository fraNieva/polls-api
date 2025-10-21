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

# Import models to register them with SQLAlchemy
from app.models import user, polls as poll_models

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Polls API", version="1.0.0")
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(polls.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Polls API!"}