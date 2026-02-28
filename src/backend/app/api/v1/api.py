from fastapi import APIRouter
from . import test, auth, users, dashboard, analysis, insights

api_router = APIRouter()

api_router.include_router(test.api_router, prefix="/test", tags=["test"])
api_router.include_router(auth.api_router, prefix="/auth", tags=["auth"])
api_router.include_router(users.api_router, prefix="/users", tags=["users"])
api_router.include_router(dashboard.api_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analysis.api_router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(insights.api_router, prefix="/insights", tags=["Insights"])