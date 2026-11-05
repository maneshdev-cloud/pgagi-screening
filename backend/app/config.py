"""Runtime configuration, all from environment variables.

Values can come from the shell or from a backend/.env file (loaded here
via python-dotenv, which is in requirements.txt).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'screening.db'}")
KB_DIR = Path(os.getenv("KB_DIR", BASE_DIR / "data" / "kb"))
SAMPLES_DIR = Path(os.getenv("SAMPLES_DIR", BASE_DIR.parent / "samples" / "resumes"))

# Optional LLM generation. If neither key is set the app runs fully offline.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

QUESTIONS_PER_SESSION = int(os.getenv("QUESTIONS_PER_SESSION", "6"))

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
