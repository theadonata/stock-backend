"""Shared FastAPI dependencies: DB session passthrough + current-user auth
guard. Single role tier — get_current_user is the only auth dependency
needed; every write/read endpoint just requires "some valid user", not a
specific permission."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# tokenUrl points at the login endpoint purely so /docs' "Authorize" button
# knows where to send credentials; it doesn't change how we verify tokens.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Resolve the bearer token to a User, or raise 401. Every non-auth
    route depends on this, which is what makes the API "login required"."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
