"""Login endpoint. No self-registration endpoint exists on purpose — per
the spec, accounts are provisioned out-of-band (the seed script creates the
one placeholder admin; additional accounts would be created the same way
or via a future admin-only endpoint, not public sign-up)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.username, payload.password)
    if user is None:
        # Deliberately generic message (not "wrong password" / "no such
        # user") to avoid revealing which part was incorrect.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)
