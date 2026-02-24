from fastapi import FastAPI
from .api.v1.api import api_router

app = FastAPI(
    title="HPE Account Intelligence API",
    description="DEveloping process",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")