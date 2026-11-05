"""End-of-session summary.

Heuristic on purpose: scores come from things we can point at - how much of
the retrieved context's vocabulary shows up in the candidate's answers,
answer depth, and coverage across topics. No black box.
"""
from .kb import tokenize


def build_summary(turns: list, profile: dict) -> dict:
    answered = [t for t in turns if t.answer.strip()]
    per_topic = {}
    total_overlap = 0.0

    for t in answered:
        ctx_terms = set(tokenize(t.context_excerpt))
        ans_terms = set(tokenize(t.answer))
        overlap = len(ctx_terms & ans_terms) / len(ctx_terms) if ctx_terms else 0.0
        total_overlap += overlap
        entry = per_topic.setdefault(t.topic, {"asked": 0, "grounding": 0.0, "words": 0})
        entry["asked"] += 1
        entry["grounding"] += overlap
        entry["words"] += len(t.answer.split())

    for entry in per_topic.values():
        entry["grounding"] = round(entry["grounding"] / entry["asked"], 3)

    n = max(len(answered), 1)
    avg_grounding = total_overlap / n
    avg_words = sum(len(t.answer.split()) for t in answered) / n
    # depth: full marks around 60+ words per answer, scaled down below that
    depth = min(avg_words / 60.0, 1.0)
    score = round(100 * (0.6 * avg_grounding + 0.4 * depth), 1)

    strong = sorted(per_topic, key=lambda k: per_topic[k]["grounding"], reverse=True)
    insights = []
    if strong:
        insights.append(f"Strongest topic: {strong[0]} (best use of the reference concepts).")
    if len(strong) > 1 and per_topic[strong[-1]]["grounding"] < 0.08:
        insights.append(f"Thin coverage on: {strong[-1]} - answers stayed generic there.")
    unprobed = [s for s in profile.get("all_skills", []) if s not in " ".join(per_topic).lower()]
    if unprobed:
        insights.append("Resume skills not covered in this session: " + ", ".join(unprobed[:5]) + ".")
    if avg_words < 20:
        insights.append("Answers were very short overall - hard to judge depth from this session.")
    insights.append(f"Answered {len(answered)} of {len(turns)} questions across {len(per_topic)} topics.")

    return {
        "score": score,
        "avg_grounding": round(avg_grounding, 3),
        "avg_answer_words": round(avg_words, 1),
        "topics": per_topic,
        "insights": insights,
    }
