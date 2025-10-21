from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

from app.core.constants import AuthConfig

# Load environment variables from a .env file
load_dotenv()

# Get the secret key from the environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = AuthConfig.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES

# Configure password context with proper bcrypt settings for Python 3.14 compatibility
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12,  # Explicit rounds for bcrypt
    bcrypt__default_ident="2b"  # Use 2b variant for better compatibility
)

# Password hashing
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback verification for direct bcrypt hashes
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Ensure password is not longer than 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate password to 72 bytes, ensuring valid UTF-8
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback to a simpler bcrypt approach if passlib fails
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Alias for compatibility with tests
def hash_password(password: str) -> str:
    """Alias for get_password_hash to maintain compatibility"""
    return get_password_hash(password)

# JWT token creation and verification
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt