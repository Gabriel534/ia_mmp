from fastapi import FastAPI

from app.routes import api_router

app = FastAPI(
    title="IA API",
    description="API de recomendacao educacional com consulta SQL e resposta via LLM",
    version="2.0.0",
)

app.include_router(api_router)
