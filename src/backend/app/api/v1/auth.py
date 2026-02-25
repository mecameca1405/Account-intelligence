from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies.deps import get_db
from ...core.security import hash_password, verify_password, create_token

from ...schemas.auth import SignUpRequest, SignInRequest, TokenResponse
from ...crud.user import user_crud
from ...models.user_role import UserRole
from ...models.region import Region
from sqlalchemy import select


router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================
# SIGN UP
# =========================
@router.post("/signup", response_model=TokenResponse)
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

    # Validate role
    role_result = await db.execute(
        select(UserRole).where(UserRole.id == data.role_id)
    )
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

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
        "role_id": data.role_id,
        "region_id": data.region_id
    }

    user = await user_crud.create(db, user_dict)

    # Create token with role name
    access_token = create_token(
        sub=user.email,
        role_name=role.name
    )

    return TokenResponse(access_token=access_token)


# =========================
# SIGN IN
# =========================
@router.post("/signin", response_model=TokenResponse)
async def sign_in(
    data: SignInRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """

    user = await user_crud.get_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_token(
        sub=user.email,
        role_name=user.role_obj.name
    )

    return TokenResponse(access_token=access_token)