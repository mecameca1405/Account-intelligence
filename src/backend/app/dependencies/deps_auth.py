from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import verify_token
from ..crud.user import user_crud
from .deps import get_db  # AsyncSession dependency

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
    token: str = Depends(oauth2_schema),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve current user from JWT token"""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = verify_token(token)  # Verify JWT
        if payload is None:
            raise cred_exc

        email: str | None = payload.get("sub")
        if email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc

    # Async query using CRUD model
    result = await db.execute(
        user_crud.model.__table__.select().where(user_crud.model.email == email)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise cred_exc

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