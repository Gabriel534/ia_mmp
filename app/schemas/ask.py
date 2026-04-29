from typing import Any

from pydantic import BaseModel, Field

class AskPayload(BaseModel):
    student_metrics: dict[str, Any] | None = None
    question: str = Field(..., min_length=1)