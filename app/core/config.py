import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_DIR = Path(__file__).resolve().parents[1]
API_DIR = APP_DIR.parent
BASE_DIR = API_DIR.parent
DATA_DIR = BASE_DIR / "data"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

SQL_SEARCH_LIMIT = int(os.getenv("SQL_SEARCH_LIMIT", "9"))
