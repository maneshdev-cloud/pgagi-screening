# Project Explanation - Role-Based Candidate Screening System

**Author:** Manesh Sunil Jadhav
**For:** PGAGI - AI/ML & Backend Engineering Intern assignment
**Repo:** https://github.com/maneshdev-cloud/pgagi-screening

## The problem

Screening interns by hand is slow and inconsistent: a resume gets skimmed,
the interviewer asks whatever comes to mind, and two candidates for the
same role end up answering completely different questions. This system makes
the first screening round structured and evidence-based:

1. It reads the candidate's actual resume.
2. It combines what the resume claims with what the role needs.
3. It asks questions drawn from a curated knowledge base - and can show,
   for every question, exactly which knowledge-base note it came from.
4. It stores the whole conversation and writes a structured summary.

## End-to-end flow

**1. Resume upload and parsing.** The candidate uploads a PDF or pastes
text and selects a role (Machine Learning Engineer Intern, AI/ML Backend
Developer Intern, or Full Stack Developer Intern). PDF text is extracted
with pypdf. A dictionary-based extractor then pulls out skills,
technologies and domain exposure (for example: "TensorFlow" as a
technology, "healthcare" as a domain, from a clinic project). Dictionary
extraction was chosen over a learned NER model because it is predictable -
when it misses something you add an alias, not a training run.

**2. Dynamic query construction.** The retrieval query is not typed by
anyone. It is assembled from the parsed profile (every extracted skill and
domain) plus the role's focus topics and key skills. The query string is
stored on the session, so the retrieval step can be audited later: you can
see exactly why the system picked the material it picked.

**3. RAG over a role-specific knowledge base.** The knowledge base is 12
short markdown notes, one per topic (decision trees, model evaluation,
FastAPI, SQL, RAG systems, and so on). The ML notes paraphrase standard
textbook material - Mitchell's *Machine Learning* is the primary source -
in original wording, and every note carries its source label. Notes are
indexed with TF-IDF and matched to the query with cosine similarity. Each
note also contains probe questions written for that topic.

**4. Grounded question generation.** For each top retrieved chunk the
system produces one question. If an LLM API key is configured, the model
rephrases a question from the chunk's content. If there is no key - the
default - the chunk's own probe question is used, prefixed with an anchor
to a skill from the candidate's resume ("Your resume mentions Python.
What does Pydantic validation buy you in FastAPI…?"). In both modes the
question row in the database stores the chunk id, the source label and the
retrieved excerpt, and the interview UI displays that grounding under the
question. Questions are therefore traceable, never free-floating.

**5. Interactive session with continuity.** Questions are asked one at a
time; answers are stored against the session. If an answer is substantial
(25+ words), the system asks one follow-up from the same chunk before
moving on - a simple rule, but it makes the session feel like a
conversation instead of a form, and it probes depth where the candidate
claims depth.

**6. Structured summary.** When the plan is exhausted (or the session is
finished early), the summary service scores the session from stored data
only: per-topic *grounding* (how much of the retrieved context's vocabulary
appears in the candidate's answers), answer depth, topic coverage, and
plain-language insights - including resume skills the session never got to
probe. The score is a weighted blend of grounding (60%) and depth (40%).
Every number can be explained from the turns table; there is no opaque
model judgement anywhere in the scoring path.

## Architecture

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js (React, TypeScript) | Required by the brief; single-page flow keeps the demo simple |
| Backend | FastAPI (Python) | Required by the brief; Pydantic validation at the edge, automatic OpenAPI docs |
| Database | SQLite via SQLAlchemy | Zero setup for a demo; the ORM layer makes Postgres a one-line `DATABASE_URL` change |
| Retrieval | TF-IDF + cosine, hand-rolled | Offline, deterministic, explainable; right size for a curated KB |
| Generation | Optional Groq/OpenAI, KB-probe fallback | The demo can never be broken by a missing key |

## Data model

- **Role** - title, description, focus topics, key skills.
- **Resume** - candidate name, raw text, extracted skills/technologies/domains.
- **Session** - resume + role, the stored plan (including the dynamic
  query), status, and the final summary JSON.
- **Turn** - one question/answer pair with topic, source chunk, retrieved
  excerpt and a follow-up flag.

## Testing

Nine pytest tests cover the parts that matter: parser extraction, KB
loading (every chunk must have a source and probe questions), retrieval
ranking (a decision-tree query must rank the decision-tree note first, a
RAG query must rank the RAG note first), question-plan grounding (every
planned question must point at a real chunk and carry context), the
follow-up rule, summary scoring, and one full API session end to end.

## Trade-offs and what I would do next

- TF-IDF ranks words, not meaning. With a KB of thousands of chunks I would
  switch to embeddings + a vector store, keeping the same grounding fields.
- The follow-up rule is length-based. A better version would check whether
  the answer actually engaged with the chunk's key terms (the grounding
  metric already computes this and could drive it).
- Answer scoring is heuristic by design for this assignment - explainable
  beats impressive here. A production version would add a calibrated
  rubric-based review, with the heuristic kept as a sanity check.
- Authentication, rate limiting and multi-interviewer dashboards are out
  of scope for a 48-hour assignment build.
