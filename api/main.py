from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Receiver API",
    description="API simples para receber dados enviados por outro serviço.",
    version="1.0.0",
)


class Payload(BaseModel):
    source: str | None = None
    event: str | None = None
    data: dict[str, Any] | list[Any] | str | int | float | bool | None = None


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "API no ar"}


@app.post("/receive")
def receive(payload: Payload) -> dict[str, Any]:
    return {
        "received": True,
        "source": payload.source,
        "event": payload.event,
        "data": payload.data,
    }
