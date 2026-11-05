"""Seed roles if the table is empty."""
from .db import SessionLocal
from .models import Role

ROLES = [
    {
        "title": "Machine Learning Engineer Intern",
        "description": "Build and evaluate ML models, work with real datasets end to end.",
        "focus_topics": "machine learning, decision trees, neural networks, model evaluation, naive bayes, instance based learning",
        "key_skills": "python, machine learning, scikit-learn, tensorflow, statistics",
    },
    {
        "title": "AI/ML Backend Developer Intern",
        "description": "Python APIs that serve ML features - FastAPI, databases, LLM/RAG integrations.",
        "focus_topics": "fastapi, rest api design, sql databases, rag systems, machine learning",
        "key_skills": "python, fastapi, sql, rest api, rag, llm",
    },
    {
        "title": "Full Stack Developer Intern",
        "description": "React/Next.js frontends backed by Python APIs and a real database.",
        "focus_topics": "react, next.js, rest api design, sql databases, fastapi",
        "key_skills": "react, next.js, typescript, python, fastapi, sql",
    },
]


def seed_roles():
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            for r in ROLES:
                db.add(Role(**r))
            db.commit()
    finally:
        db.close()
