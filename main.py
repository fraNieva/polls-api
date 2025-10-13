from fastapi import FastAPI
from app.db.database import engine, Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Polls API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Polls API!"}