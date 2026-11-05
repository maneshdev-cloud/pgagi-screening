"""Question planning.

Flow:
1. Build a dynamic query from the parsed resume + the selected role
   (candidate skills x role focus topics). This is deliberately visible -
   the plan stores the query so anyone can see why these chunks came back.
2. Retrieve the top KB chunks for that query.
3. Turn chunks into questions. If an LLM key is configured we ask the model
   to phrase a question from the chunk; on any failure (or no key) we fall
   back to the chunk's own probe questions, anchored to a skill the
   candidate actually listed. Either way the question keeps a pointer to
   its source chunk, so grounding is inspectable in the UI and the DB.
"""
import json
import urllib.request

from .. import config


def build_query(profile: dict, role) -> str:
    parts = []
    parts.extend(profile.get("all_skills", []))
    parts.extend(role.focus_topics.split(","))
    parts.extend(role.key_skills.split(","))
    parts.extend(profile.get("domains", []))
    return " ".join(p.strip() for p in parts if p and p.strip())


def _anchor(profile: dict, chunk) -> str:
    """Pick a candidate skill that overlaps this chunk, for the opener."""
    chunk_terms = set(chunk.topics) | set(chunk.title.lower().split())
    for skill in profile.get("all_skills", []):
        if skill in chunk_terms or any(w in chunk.title.lower() for w in skill.split()):
            return skill
    return ""


def _llm_question(chunk, profile: dict, role) -> str | None:
    """Try to phrase a question with an LLM. Returns None on any problem."""
    api_key = config.GROQ_API_KEY or config.OPENAI_API_KEY
    if not api_key:
        return None
    if config.GROQ_API_KEY:
        url, model = "https://api.groq.com/openai/v1/chat/completions", config.LLM_MODEL
    else:
        url, model = "https://api.openai.com/v1/chat/completions", "gpt-4o-mini"
    prompt = (
        f"You are screening a candidate for the role '{role.title}'. "
        f"The candidate's resume mentions: {', '.join(profile.get('all_skills', []))}. "
        f"Using ONLY the reference note below, write one specific interview question "
        f"that tests understanding of it. No preamble, just the question.\n\n"
        f"Reference note ({chunk.title}): {chunk.body[:1200]}"
    )
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"].strip()
        return text if text.endswith("?") or len(text) > 20 else None
    except Exception:
        return None


def build_plan(profile: dict, role, retriever, total: int = None) -> dict:
    """Create the question plan for a session."""
    total = total or config.QUESTIONS_PER_SESSION
    query = build_query(profile, role)
    hits = retriever.search(query, top_k=total + 3)

    plan = []
    used_questions = set()
    for chunk, score in hits:
        if len(plan) >= total:
            break
        question = _llm_question(chunk, profile, role)
        generated_by = "llm"
        if not question:
            generated_by = "kb-probe"
            question = next((q for q in chunk.questions if q not in used_questions), None)
            if not question:
                continue
            anchor = _anchor(profile, chunk)
            if anchor and anchor not in question.lower():
                question = f"Your resume mentions {anchor}. {question}"
        used_questions.add(question)
        plan.append({
            "question": question,
            "topic": chunk.title,
            "source_chunk": f"{chunk.id} ({chunk.source})",
            "context_excerpt": chunk.body[:400],
            "retrieval_score": score,
            "generated_by": generated_by,
        })
    return {"query": query, "questions": plan}


def _strip_anchor(question: str) -> str:
    """Remove the 'Your resume mentions X.' opener build_plan may have added,
    so an asked question can be compared with the raw probe questions."""
    prefix = "Your resume mentions "
    if question.startswith(prefix):
        dot = question.find(". ")
        if dot != -1:
            return question[dot + 2:]
    return question


def pick_followup(answer: str, chunk_questions: list, asked: set) -> str | None:
    """A follow-up is just the next unused probe question on the same chunk,
    chosen when the answer is long enough to suggest the candidate can go
    deeper. Simple, but it keeps the session continuous."""
    if len(answer.split()) < 25:
        return None
    asked_plain = {_strip_anchor(q) for q in asked}
    for q in chunk_questions:
        if q not in asked_plain:
            return q
    return None
