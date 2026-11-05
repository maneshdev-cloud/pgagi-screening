"""Runtime configuration, all from environment variables."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'screening.db'}")
KB_DIR = Path(os.getenv("KB_DIR", BASE_DIR / "data" / "kb"))
SAMPLES_DIR = Path(os.getenv("SAMPLES_DIR", BASE_DIR.parent / "samples" / "resumes"))

# Optional LLM generation. If neither key is set the app runs fully offline.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

QUESTIONS_PER_SESSION = int(os.getenv("QUESTIONS_PER_SESSION", "6"))

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
