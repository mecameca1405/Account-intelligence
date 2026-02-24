from fastapi import APIRouter


api_router = APIRouter()

@api_router.get("/response")
def obtener_categorias():
    return {"Respones": "Endpoint working"}