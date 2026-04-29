import json
import re
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

from app.core.config import LLM_MODEL, SQL_SEARCH_LIMIT
from app.core.prompts import SQL_GENERATION_PROMPT, SYSTEM_PROMPT
from app.repositories.database_repository import DatabaseRepository


class RagService:
    def __init__(self):
        self.database_repository = DatabaseRepository()

    def ask(self, question: str, student_metrics: dict[str, Any]) -> str:
        return self.build_chain().invoke(
            {
                "question": question,
                "student_metrics": student_metrics,
            }
        )

    def build_chain(self):
        llm = ChatGroq(model_name=LLM_MODEL, temperature=0)
        recommendation_prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

        return (
            {
                "context": RunnableLambda(self.build_context_from_sql),
                "question": RunnableLambda(lambda payload: payload["question"]),
                "student_metrics": RunnableLambda(lambda payload: payload["student_metrics"]),
            }
            | recommendation_prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(self.clean_response)
        )

    def build_context_from_sql(self, payload: dict[str, Any]) -> str:
        queries = self.build_sql_queries(
            question=payload["question"],
            student_metrics=payload["student_metrics"],
        )
        results = self.database_repository.execute_resource_queries(
            queries=queries,
            limit=SQL_SEARCH_LIMIT,
        )
        return self.format_query_results(queries=queries, results=results)

    def build_sql_queries(self, question: str, student_metrics: dict[str, Any]) -> dict[str, str | None]:
        llm = ChatGroq(model_name=LLM_MODEL, temperature=0)
        sql_prompt = ChatPromptTemplate.from_template(SQL_GENERATION_PROMPT)
        raw_response = (
            sql_prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(self.clean_response)
        ).invoke(
            {
                "question": question,
                "student_metrics": json.dumps(student_metrics, ensure_ascii=True, indent=2),
                "sql_limit": SQL_SEARCH_LIMIT,
            }
        )

        parsed_response = self.parse_sql_queries(raw_response)
        print(raw_response)
        return {
            "videos_query": parsed_response.get("videos_query"),
            "literature_query": parsed_response.get("literature_query"),
            "disciplines_query": parsed_response.get("disciplines_query"),
        }

    def parse_sql_queries(self, raw_response: str) -> dict[str, str | None]:
        normalized_response = raw_response.strip()
        if normalized_response.startswith("```"):
            normalized_response = re.sub(r"^```(?:json)?", "", normalized_response).strip()
            normalized_response = re.sub(r"```$", "", normalized_response).strip()

        try:
            parsed = json.loads(normalized_response)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Falha ao interpretar JSON de queries SQL: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError("O gerador de SQL deve retornar um objeto JSON")

        return parsed

    def format_query_results(self, queries: dict[str, str | None], results: dict[str, list[dict]]) -> str:
        parts: list[str] = []
        for key in ("disciplines_query", "videos_query", "literature_query"):
            rows = results.get(key, [])
            query = queries.get(key)
            if not query and not rows:
                continue

            label = key.replace("_query", "")
            parts.append(f"Categoria: {label}")
            if query:
                parts.append(f"Query executada:\n{query.strip()}")
            if rows:
                parts.append("Resultados:")
                parts.append(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
            else:
                parts.append("Resultados:\n[]")

        return "\n\n".join(parts) if parts else "Nenhum contexto relevante encontrado."

    def clean_response(self, text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
