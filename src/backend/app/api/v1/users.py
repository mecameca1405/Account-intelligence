from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...dependencies.deps_auth import get_current_user
from ...schemas.me_response import MeResponse
from ...schemas.user import AdminUserUpdate, SelfUserUpdate
from ...core.security import hash_password
from ...dependencies.deps_auth import require_role
from ...dependencies.deps import get_db
from ...models.user import User
from ...crud.user import user_crud
from ...core.roles import Roles
from datetime import datetime, timezone
from ...crud.session import revoke_all_user_sessions

api_router = APIRouter()

@api_router.get("/me", response_model=MeResponse)
async def get_me(current_user = Depends(get_current_user)):

    return MeResponse(
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.name,
        region=current_user.region.name,
    )

@api_router.patch("/users/{user_id}")
async def update_user_admin(
    user_id: int,
    data: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(Roles.ADMIN))
):

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    password_changed = False
    security_sensitive_change = False

    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data["updated_by"] = current_user.id

    # Password change
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
        password_changed = True
        security_sensitive_change = True

    # Role change affects permissions
    if "role_id" in update_data and update_data["role_id"] != user.role_id:
        security_sensitive_change = True

    # Region change (if region affects authorization logic)
    if "region_id" in update_data and update_data["region_id"] != user.region_id:
        security_sensitive_change = True

    # Email change affects JWT sub
    if "email" in update_data and update_data["email"] != user.email:
        security_sensitive_change = True

    # is_active change
    if "is_active" in update_data and update_data["is_active"] != user.is_active:
        security_sensitive_change = True

    update_data.pop("id", None)
    update_data.pop("created_at", None)

    updated_user = await user_crud.update(db, user, update_data)

    # Access token invalidation
    if security_sensitive_change:
        updated_user.token_version += 1
        await db.commit()

    # Refresh token invalidation
    if password_changed or security_sensitive_change:
        await revoke_all_user_sessions(db, user.id)  # FIXED (was current_user.id)

    return {"message": "User updated successfully"}


@api_router.patch("/users/me")
async def update_me(
    data: SelfUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    password_changed = False
    security_sensitive_change = False

    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    update_data["updated_by"] = current_user.id

    # Password change
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
        password_changed = True
        security_sensitive_change = True

    # Email change affects JWT sub
    if "email" in update_data and update_data["email"] != current_user.email:
        security_sensitive_change = True

    # Fields self cannot modify
    forbidden_fields = {"role_id", "region_id", "id", "created_at", "token_version"}
    for field in forbidden_fields:
        update_data.pop(field, None)

    updated_user = await user_crud.update(db, current_user, update_data)

    # Access token invalidation
    if security_sensitive_change:
        updated_user.token_version += 1
        await db.commit()

    # Refresh token invalidation
    if password_changed or security_sensitive_change:
        await revoke_all_user_sessions(db, current_user.id)

    return {"message": "Profile updated successfully"}


@api_router.delete("/users/{user_id}")
async def soft_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    user.updated_by = current_user.id

    await db.commit()

    return {"message": "User soft deleted"}