"""Tests for parsing, retrieval, question planning and the API flow."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import kb as kb_service          # noqa: E402
from app.services import parser as resume_parser    # noqa: E402
from app.services import questions as q             # noqa: E402
from app.services import summary as summary_service  # noqa: E402

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "kb"


class FakeRole:
    title = "Machine Learning Engineer Intern"
    focus_topics = "machine learning, decision trees, model evaluation"
    key_skills = "python, machine learning, scikit-learn"


ML_RESUME = """
Jane Doe - Python, Machine Learning, Scikit-learn, TensorFlow, SQL.
Built a text classification project with Naive Bayes and cross-validation.
Freelance data analysis for a healthcare clinic booking app.
"""


def test_parser_finds_skills_and_domains():
    profile = resume_parser.parse_resume(ML_RESUME)
    assert "machine learning" in profile["all_skills"]
    assert "tensorflow" in profile["technologies"]
    assert "sql" in profile["technologies"]
    assert "healthcare" in profile["domains"]


def test_parser_handles_empty_text():
    profile = resume_parser.parse_resume("hello world")
    assert profile["all_skills"] == []
    assert profile["word_count"] == 2


def test_kb_loads_with_sources_and_questions():
    chunks = kb_service.load_chunks(KB_DIR)
    assert len(chunks) >= 10
    for chunk in chunks:
        assert chunk.questions, f"{chunk.id} has no probe questions"
        assert chunk.source, f"{chunk.id} has no source label"


def test_retrieval_ranks_decision_trees_for_tree_query():
    chunks = kb_service.load_chunks(KB_DIR)
    retriever = kb_service.Retriever(chunks)
    hits = retriever.search("decision tree information gain entropy split", top_k=3)
    assert hits, "retrieval returned nothing"
    assert hits[0][0].id == "decision-trees"


def test_retrieval_ranks_rag_for_rag_query():
    chunks = kb_service.load_chunks(KB_DIR)
    retriever = kb_service.Retriever(chunks)
    hits = retriever.search("rag retrieval augmented generation embeddings chunking llm", top_k=3)
    assert hits[0][0].id == "rag-systems"


def test_plan_questions_are_grounded_in_chunks():
    chunks = kb_service.load_chunks(KB_DIR)
    retriever = kb_service.Retriever(chunks)
    profile = resume_parser.parse_resume(ML_RESUME)
    plan = q.build_plan(profile, FakeRole(), retriever, total=4)
    assert plan["query"], "plan must record the dynamic query"
    assert len(plan["questions"]) == 4
    chunk_ids = {c.id for c in chunks}
    for item in plan["questions"]:
        assert item["source_chunk"].split(" ")[0] in chunk_ids
        assert item["context_excerpt"], "each question must carry retrieved context"
        assert item["generated_by"] in ("kb-probe", "llm")


def test_followup_needs_a_substantial_answer():
    qs = ["First?", "Second?"]
    assert q.pick_followup("too short", qs, {"First?"}) is None
    long_answer = " ".join(["word"] * 30)
    assert q.pick_followup(long_answer, qs, {"First?"}) == "Second?"


def test_summary_scores_and_insights():
    class T:
        def __init__(self, topic, ctx, ans):
            self.topic, self.context_excerpt, self.answer = topic, ctx, ans

    turns = [
        T("Decision Trees", "information gain entropy split attribute",
          "Information gain measures how much a split reduces entropy of the labels, so the attribute with the highest gain is chosen at each node of the tree."),
        T("Model Evaluation", "cross validation test set overfitting",
          "I would use cross validation and keep a separate test set to check overfitting before trusting the score."),
    ]
    result = summary_service.build_summary(turns, {"all_skills": ["python", "machine learning", "rust"]})
    assert 0 <= result["score"] <= 100
    assert result["topics"]["Decision Trees"]["asked"] == 1
    assert any("rust" in i for i in result["insights"])
