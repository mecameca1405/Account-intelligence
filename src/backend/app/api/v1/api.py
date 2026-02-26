from fastapi import APIRouter
from . import test, auth, users

api_router = APIRouter()

api_router.include_router(test.api_router, prefix="/test", tags=["test"])
api_router.include_router(auth.api_router, prefix="/auth", tags=["auth"])
api_router.include_router(users.api_router, prefix="/users", tags=["users"])