from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.v1.endpoints import users, auth, polls

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Polls API", version="1.0.0")
app.include_router(users.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(polls.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Polls API!"}