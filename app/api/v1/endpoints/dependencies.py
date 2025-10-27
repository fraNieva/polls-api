from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from the database.
    Any endpoint that requires authentication can use this dependency.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception
    
    return user


def get_current_user_optional(
    db: Session = Depends(get_db), 
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False))
) -> Optional[User]:
    """Get the current user from the database, but don't raise an error if no token is provided.
    Returns None if no valid authentication is provided.
    This is useful for endpoints that work differently based on authentication status.
    """
    if token is None:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    
    except JWTError:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user
