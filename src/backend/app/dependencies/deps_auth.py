from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.user import User
from sqlalchemy.orm import selectinload
from ..core.security import verify_token
from ..models.user import User
from sqlalchemy import select
from .deps import get_db  # AsyncSession dependency

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:

    token = credentials.credentials

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email: str = payload["sub"]

    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.region))
        .where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def require_admin(
    current_user = Depends(get_current_user)
):
    """Check if current user has admin role"""
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: admin role required"
        )
    return current_user