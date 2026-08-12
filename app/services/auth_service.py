"""Auth business logic: verifying credentials and looking up users."""
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Return the User if username/password match, else None. Callers turn
    a None into a 401 — we never leak whether it was the username or
    password that was wrong, to avoid username enumeration."""
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
