from fastapi import APIRouter

from app.controllers.health_controller import router as health_router
from app.controllers.rag_controller import router as rag_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(rag_router, tags=["rag"])

