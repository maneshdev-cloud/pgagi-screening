# Role-Based Candidate Screening System

An AI-powered screening tool built for the PGAGI AI/ML & Backend Intern
assignment. A candidate uploads a resume and picks a role; the system parses
the resume, builds a query from what it finds, retrieves matching material
from a knowledge base, and runs a short interview whose questions are
grounded in the retrieved material. Every answer is stored, and the session
ends with a structured summary.

**Stack:** Next.js (React + TypeScript) frontend · FastAPI (Python) backend ·
SQLite via SQLAlchemy · TF-IDF retrieval · optional LLM question phrasing
with a deterministic offline fallback.

---

## Quick start

You need Python 3.11+ and Node 18+.

**Backend** (terminal 1):

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000
```

Open http://localhost:3000, upload a resume (or click a sample resume), pick
a role, and start the session. No API key is needed - without one the system
runs in its offline mode.

**Tests:**

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests/ -q      # 9 tests: parsing, retrieval, planning, API flow
```

## How it works

```
Resume (PDF/text) ──► Parser ──► profile {skills, technologies, domains}
                                      │
Role (focus topics + key skills) ─────┤
                                      ▼
                          Dynamic query construction
                                      │
                                      ▼
              RAG retrieval (TF-IDF over the knowledge base)
                                      │
                                      ▼
        Question plan - every question points at its source chunk
                                      │
                                      ▼
        Interview session (Q -> A -> optional follow-up, all stored)
                                      │
                                      ▼
              Structured summary: per-topic grounding + insights
```

1. **Parsing** (`backend/app/services/parser.py`) - PDFs are read with
   pypdf; skills/technologies are extracted with a curated alias dictionary
   and domains from keyword groups. Predictable and unit-tested rather than
   a black-box NER model.
2. **Dynamic query construction** (`services/questions.py`) - the query is
   literally the candidate's extracted skills + the role's focus topics +
   detected domains, and it is stored on the session so the retrieval is
   auditable.
3. **Retrieval** (`services/kb.py`) - the knowledge base is a set of small
   markdown notes, one per topic, each carrying a source label and its own
   probe questions. Retrieval is TF-IDF + cosine similarity, implemented
   directly (no external vector service) so it runs anywhere.
4. **Question generation** - if `GROQ_API_KEY` or `OPENAI_API_KEY` is set,
   an LLM phrases a question from the retrieved chunk. If not - or if the
   call fails - the chunk's own probe question is used, anchored to a skill
   from the candidate's resume. Either way, the question record keeps its
   source chunk id, source label and the retrieved excerpt, and the UI shows
   that grounding next to the question.
5. **Session continuity** - answers are stored per turn; a substantial
   answer (25+ words) can trigger one follow-up drawn from the same chunk
   before the plan moves on.
6. **Summary** (`services/summary.py`) - heuristic and explainable: how much
   of the retrieved context's vocabulary the candidate actually used
   (grounding), answer depth, and per-topic coverage, plus plain-language
   insights including resume skills the session never probed.

## Knowledge base

`backend/data/kb/` holds 12 topic notes: supervised learning, decision
trees, neural networks, model evaluation, Naive Bayes, instance-based
learning, feature engineering, FastAPI, REST design, SQL, React/Next.js,
and RAG systems. The ML notes paraphrase standard textbook material -
Mitchell's *Machine Learning* is the primary reference - in original words;
no textbook text is reproduced. Each note keeps its source label, which is
what the UI displays as the question's grounding.

## Configuration

All configuration is via environment variables - see `.env.example`.
`DATABASE_URL`, `KB_DIR`, `QUESTIONS_PER_SESSION`, `FRONTEND_ORIGIN`, and
optionally `GROQ_API_KEY` / `OPENAI_API_KEY` / `LLM_MODEL`.

## Project layout

```
backend/
  app/
    main.py          API routes (roles, parsing, sessions, summary)
    models.py        Role, Resume, Session, Turn tables
    seed.py          the three seeded roles
    services/
      parser.py      resume text extraction + profile
      kb.py          KB loading + TF-IDF retriever
      questions.py   query construction + question planning + follow-ups
      summary.py     session scoring and insights
  data/kb/           knowledge-base notes (markdown)
  tests/             pytest suite
frontend/            Next.js app (single-page flow: setup -> interview -> summary)
samples/resumes/     sample resumes (text + PDF) for an instant demo
docs/PROJECT.md      longer write-up of design decisions and trade-offs
```

## Design decisions, briefly

- **TF-IDF instead of embeddings** - deterministic, offline, zero extra
  dependencies, and easy to explain. With 12 curated chunks it ranks
  correctly; embeddings would be the upgrade path for a KB in the thousands.
- **Grounding is a data property, not a promise** - the source chunk and
  excerpt are stored in the database with every question, so any question
  can be traced back after the fact.
- **Offline-first generation** - the demo can never be broken by a missing
  or expired API key; the LLM only rephrases, it never decides what to ask.
- **Heuristic summary scoring** - every number in the summary can be
  explained from the stored turns; no opaque model judgement.
