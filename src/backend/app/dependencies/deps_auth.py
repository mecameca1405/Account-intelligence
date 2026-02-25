from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..models.user import User
from sqlalchemy.orm import selectinload
from ..core.security import verify_token
from ..models.user import User
from sqlalchemy import select
from .deps import get_db

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:

    token = credentials.credentials

    # Decode and validate JWT
    payload = verify_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    email: str = payload.get("sub")
    token_version: int = payload.get("token_version")

    # Fetch user with eager-loaded relationships to avoid lazy loading in async context
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.role),
            selectinload(User.region)
        )
        .where(User.email == email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Ensure user is active (soft delete / suspension check)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Validate token version to enforce immediate token revocation
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    return user


def require_role(required_role: str):
    """
    Dependency factory to require a specific role.
    Usage: Depends(require_role("admin"))
    """
    
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:

        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker