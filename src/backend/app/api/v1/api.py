from fastapi import APIRouter
from . import test

api_router = APIRouter()

api_router.include_router(test.api_router, prefix="/test", tags=["test"])