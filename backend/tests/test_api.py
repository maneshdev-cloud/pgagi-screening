"""End-to-end API test: role list -> create session -> answer -> summary."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DATABASE_URL"] = "sqlite:///./test_screening.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

RESUME = """
Alex Ray - Python, Machine Learning, Scikit-learn, FastAPI, SQL, React.
Built an NLP text classification service with a FastAPI backend and a
PostgreSQL database. Comfortable with cross-validation and REST API design.
"""


def test_full_session_flow():
    with client:
        roles = client.get("/api/roles").json()
        assert roles, "roles must be seeded"
        role_id = roles[0]["id"]

        created = client.post("/api/sessions", json={
            "candidate_name": "Alex Ray", "role_id": role_id, "resume_text": RESUME,
        })
        assert created.status_code == 200, created.text
        session = created.json()
        assert session["current_question"] is not None
        assert session["plan_query"], "dynamic query must be stored on the session"
        assert session["total_questions"] >= 3

        # answer everything; long answers may trigger a follow-up, so loop
        # generously and rely on the session reporting completion.
        view = session
        for _ in range(20):
            if view["status"] == "completed":
                break
            sid = view["id"]
            view = client.post(f"/api/sessions/{sid}/answers", json={
                "answer": "Entropy measures label impurity; a split with high information "
                          "gain reduces entropy the most, which is why ID3 chooses it, and "
                          "cross validation plus pruning keep the tree from overfitting the "
                          "training data instead of generalising to unseen examples.",
            }).json()

        assert view["status"] == "completed"
        assert view["summary"] is not None
        assert "insights" in view["summary"]
        answered = [t for t in view["turns"] if t["answer"]]
        assert answered, "answers must be stored on the session turns"
