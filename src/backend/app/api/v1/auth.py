from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from ...dependencies.deps import get_db
from ...core.security import hash_password, verify_password, create_token, create_refresh_token, verify_token, hash_refresh_token
from ...models.user_session import UserSession
from ...schemas.auth import SignUpRequest, SignInRequest, TokenResponse, RefreshRequest
from ...crud.user import user_crud
from ...models.user import User
from ...models.region import Region
from sqlalchemy import select
from ...core.roles import Roles
from ...core.config import settings



api_router = APIRouter()
security = HTTPBearer()

# =========================
# SIGN UP
# =========================
@api_router.post("/signup", response_model=TokenResponse)
async def sign_up(
    data: SignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user and return JWT token.
    """

    # Check if email already exists
    existing_user = await user_crud.get_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate region
    region_result = await db.execute(
        select(Region).where(Region.id == data.region_id)
    )
    region = region_result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=400, detail="Invalid region_id")

    # Create user
    user_dict = {
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "region_id": data.region_id
    }

    user = await user_crud.create(db, user_dict)

    # Create token with role name
    access_token = create_token(
        sub=user.email,
        role_name=Roles.USER,
        token_version=user.token_version
    )

    return TokenResponse(access_token=access_token)


# =========================
# SIGN IN
# =========================
@api_router.post("/signin", response_model=TokenResponse)
async def sign_in(
    data: SignInRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_by_email(db, data.email)

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_token(
        sub=user.email,
        role_name=user.role.name,
        token_version=user.token_version
    )

    refresh_token = create_refresh_token(user.email)

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        device=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRE_DAYS),
    )

    db.add(session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@api_router.post("/refresh")
async def refresh(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    token = data.refresh_token
    payload = verify_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token")

    token_hash = hash_refresh_token(token)

    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token_hash == token_hash,
            UserSession.revoked == False
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")

    # ROTATION
    session.revoked = True

    user_result = await db.execute(
        select(User).where(
            User.id == session.user_id,
            User.is_deleted == False
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_token(payload["sub"], user.role.name)
    new_refresh = create_refresh_token(payload["sub"])

    new_session = UserSession(
        user_id=session.user_id,
        refresh_token_hash=hash_refresh_token(new_refresh),
        device=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(new_session)
    await db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }


@api_router.post("/logout")
async def logout(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    token = data.refresh_token
    token_hash = hash_refresh_token(token)

    result = await db.execute(
        select(UserSession).where(
            UserSession.refresh_token_hash == token_hash
        )
    )

    session = result.scalar_one_or_none()

    if not session or session.revoked:
        raise HTTPException(status_code=401, detail="Invalid session")

    session.revoked = True
    await db.commit()

    return {"message": "Logged out successfully"}