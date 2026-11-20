"""FastAPI dependency injection utilities."""

from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return User if valid Bearer token provided, otherwise None."""
    if not auth:
        return None
    token = auth.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """Enforce authenticated user requirement."""
    if not user:
        raise UnauthorizedException("Authentication token required or expired")
    return user
