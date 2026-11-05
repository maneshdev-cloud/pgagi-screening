"""PGAGI screening system - API entry point.

Run:  uvicorn app.main:app --reload --port 8000
"""
import json

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from . import config
from .db import get_db, init_db
from .models import Resume, Role, Session, Turn
from .seed import seed_roles
from .services import kb as kb_service
from .services import parser as resume_parser
from .services import questions as question_service
from .services import summary as summary_service

app = FastAPI(title="Role-Based Candidate Screening System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_chunks = kb_service.load_chunks(config.KB_DIR)
_retriever = kb_service.Retriever(_chunks)


@app.on_event("startup")
def _startup():
    init_db()
    seed_roles()


# ---------- roles & samples ----------

@app.get("/api/roles")
def list_roles(db: DbSession = Depends(get_db)):
    return [
        {"id": r.id, "title": r.title, "description": r.description,
         "key_skills": [s.strip() for s in r.key_skills.split(",") if s.strip()]}
        for r in db.query(Role).all()
    ]


@app.get("/api/samples")
def list_samples():
    out = []
    if config.SAMPLES_DIR.exists():
        for p in sorted(config.SAMPLES_DIR.glob("*.txt")):
            out.append({"name": p.stem.replace("_", " ").title(), "text": p.read_text(encoding="utf-8")})
    return out


@app.get("/api/kb")
def list_kb():
    """Show the knowledge base so the retrieval grounding is inspectable."""
    return [
        {"id": c.id, "title": c.title, "topics": c.topics, "source": c.source,
         "probe_questions": c.questions}
        for c in _chunks
    ]


# ---------- resume parsing ----------

@app.post("/api/resumes/parse")
async def parse_upload(file: UploadFile = File(None), text: str = Form("")):
    if file is not None and file.filename:
        raw = resume_parser.extract_text_from_upload(file.filename, await file.read())
    elif text.strip():
        raw = text.strip()
    else:
        raise HTTPException(400, "Provide a resume file or paste resume text.")
    if len(raw) < 40:
        raise HTTPException(400, "Could not extract enough text from that resume.")
    return {"text": raw, "profile": resume_parser.parse_resume(raw)}


# ---------- sessions ----------

class SessionIn(BaseModel):
    candidate_name: str = "Candidate"
    role_id: int
    resume_text: str


def _session_view(s: Session) -> dict:
    turns = [
        {"index": t.index, "question": t.question, "topic": t.topic,
         "source_chunk": t.source_chunk, "context_excerpt": t.context_excerpt,
         "answer": t.answer, "is_followup": bool(t.is_followup)}
        for t in s.turns
    ]
    current = turns[s.current_index] if s.status == "in_progress" and s.current_index < len(turns) else None
    return {
        "id": s.id, "status": s.status,
        "candidate_name": s.resume.candidate_name,
        "role": s.role.title,
        "profile": {
            "skills": json.loads(s.resume.skills or "[]"),
            "technologies": json.loads(s.resume.technologies or "[]"),
            "domains": json.loads(s.resume.domains or "[]"),
        },
        "plan_query": (json.loads(s.plan or "{}")).get("query", ""),
        "total_questions": len(turns),
        "current_index": s.current_index,
        "current_question": current,
        "turns": turns,
        "summary": json.loads(s.summary) if s.summary else None,
    }


@app.post("/api/sessions")
def create_session(body: SessionIn, db: DbSession = Depends(get_db)):
    role = db.get(Role, body.role_id)
    if not role:
        raise HTTPException(404, "Role not found.")
    profile = resume_parser.parse_resume(body.resume_text)
    resume = Resume(
        candidate_name=body.candidate_name or "Candidate",
        raw_text=body.resume_text,
        skills=json.dumps(profile["skills"]),
        technologies=json.dumps(profile["technologies"]),
        domains=json.dumps(profile["domains"]),
    )
    db.add(resume)
    db.flush()

    plan = question_service.build_plan(profile, role, _retriever)
    if not plan["questions"]:
        raise HTTPException(422, "Retrieval found no matching knowledge-base material for this resume/role.")

    session = Session(resume_id=resume.id, role_id=role.id, plan=json.dumps(plan))
    db.add(session)
    db.flush()
    for i, q in enumerate(plan["questions"]):
        db.add(Turn(session_id=session.id, index=i, question=q["question"], topic=q["topic"],
                    source_chunk=q["source_chunk"], context_excerpt=q["context_excerpt"]))
    db.commit()
    db.refresh(session)
    return _session_view(session)


@app.get("/api/sessions/{session_id}")
def get_session(session_id: int, db: DbSession = Depends(get_db)):
    s = db.get(Session, session_id)
    if not s:
        raise HTTPException(404, "Session not found.")
    return _session_view(s)


class AnswerIn(BaseModel):
    answer: str


@app.post("/api/sessions/{session_id}/answers")
def submit_answer(session_id: int, body: AnswerIn, db: DbSession = Depends(get_db)):
    s = db.get(Session, session_id)
    if not s or s.status != "in_progress":
        raise HTTPException(404, "Session not found or already finished.")
    if s.current_index >= len(s.turns):
        raise HTTPException(400, "No question is waiting for an answer.")
    turn = s.turns[s.current_index]
    turn.answer = body.answer.strip()

    # session continuity: a substantial answer can earn one follow-up drawn
    # from the same retrieved chunk before we move on.
    asked = {t.question for t in s.turns}
    if not turn.is_followup:
        chunk = next((c for c in _chunks if turn.source_chunk.startswith(c.id)), None)
        follow = question_service.pick_followup(turn.answer, chunk.questions if chunk else [], asked)
        if follow:
            new_turn = Turn(session_id=s.id, index=len(s.turns), question=follow,
                            topic=turn.topic, source_chunk=turn.source_chunk,
                            context_excerpt=turn.context_excerpt, is_followup=1)
            db.add(new_turn)
            s.turns.append(new_turn)
            # ask the follow-up next, then return to the planned order
            order = [t for t in s.turns]
            order.remove(new_turn)
            order.insert(s.current_index + 1, new_turn)
            for i, t in enumerate(order):
                t.index = i
            s.turns = order

    s.current_index += 1
    if s.current_index >= len(s.turns):
        return _finish(s, db)
    db.commit()
    db.refresh(s)
    return _session_view(s)


def _finish(s: Session, db: DbSession) -> dict:
    s.status = "completed"
    profile = {
        "all_skills": json.loads(s.resume.skills or "[]") + json.loads(s.resume.technologies or "[]"),
    }
    s.summary = json.dumps(summary_service.build_summary(list(s.turns), profile))
    db.commit()
    db.refresh(s)
    return _session_view(s)


@app.post("/api/sessions/{session_id}/finish")
def finish_session(session_id: int, db: DbSession = Depends(get_db)):
    s = db.get(Session, session_id)
    if not s:
        raise HTTPException(404, "Session not found.")
    if s.status == "completed":
        return _session_view(s)
    return _finish(s, db)


@app.get("/api/sessions")
def list_sessions(db: DbSession = Depends(get_db)):
    rows = db.query(Session).order_by(Session.id.desc()).limit(50).all()
    return [
        {"id": s.id, "candidate_name": s.resume.candidate_name, "role": s.role.title,
         "status": s.status, "created_at": s.created_at.isoformat() if s.created_at else ""}
        for s in rows
    ]


@app.get("/health")
def health():
    return {"ok": True, "kb_chunks": len(_chunks),
            "llm_enabled": bool(config.GROQ_API_KEY or config.OPENAI_API_KEY)}
