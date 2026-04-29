from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.ask import AskPayload
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/ask")
def rag_ask(payload: AskPayload) -> dict[str, Any]:
    try:
        answer = RagService().ask(
            question=payload.question,
            student_metrics=payload.student_metrics or {},
        )
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
