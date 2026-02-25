from fastapi import APIRouter, Depends
from ...dependencies.deps_auth import get_current_user
from ...schemas.me_response import MeResponse

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