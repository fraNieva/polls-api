from pydantic import BaseModel, EmailStr

# Define a schema for creating a new user
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    username: str
    is_active: bool = True

# Define a schema for reading user data
class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    username: str
    is_active: bool

    class Config:
        # Enable ORM mode to work with SQLAlchemy models
        from_attributes = True