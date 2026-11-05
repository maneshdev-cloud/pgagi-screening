"""Knowledge base loading + retrieval.

The KB is a folder of small markdown notes, one topic per file, written for
this project (ML notes paraphrase standard textbook material - Mitchell's
"Machine Learning" is the primary reference - in our own words).

Each file looks like:

    # Decision Trees
    topics: machine learning, decision trees
    source: Machine Learning - Tom Mitchell (Ch. 3), paraphrased notes

    ## Key points
    - ...

    ## Probe questions
    - ...

Retrieval is plain TF-IDF with cosine similarity - no external service, so
the demo works offline. Every chunk keeps its source label so the UI can
show exactly where a question came from.
"""
import math
import re
from collections import Counter
from pathlib import Path

STOPWORDS = set(
    "a an the is are was were be been of to in for on with and or as at by from "
    "it its this that these those you your we our they their he she how what why "
    "when which who can could should would do does did have has had".split()
)


def tokenize(text: str) -> list:
    words = re.findall(r"[a-z0-9][a-z0-9.+-]*", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


class Chunk:
    def __init__(self, chunk_id, title, topics, source, body, questions):
        self.id = chunk_id
        self.title = title
        self.topics = topics
        self.source = source
        self.body = body
        self.questions = questions
        self.tokens = tokenize(title + " " + " ".join(topics) + " " + body)


def load_chunks(kb_dir: Path) -> list:
    chunks = []
    for path in sorted(Path(kb_dir).glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        chunks.extend(_parse_file(path.stem, raw))
    return chunks


def _parse_file(stem: str, raw: str) -> list:
    lines = raw.splitlines()
    title, topics, source = stem, [], "Project knowledge base"
    body_lines, questions = [], []
    section = "body"
    for line in lines:
        s = line.strip()
        if s.startswith("# "):
            title = s[2:].strip()
        elif s.lower().startswith("topics:"):
            topics = [t.strip() for t in s.split(":", 1)[1].split(",") if t.strip()]
        elif s.lower().startswith("source:"):
            source = s.split(":", 1)[1].strip()
        elif s.lower().startswith("## probe questions"):
            section = "questions"
        elif s.startswith("## "):
            section = "body"
        elif s.startswith("- ") and section == "questions":
            questions.append(s[2:].strip())
        elif s and not s.startswith("#"):
            body_lines.append(s)
    body = " ".join(body_lines)
    # one chunk per file keeps the mapping question->source easy to follow
    return [Chunk(stem, title, topics, source, body, questions)]


class Retriever:
    """Tiny TF-IDF index over the KB chunks."""

    def __init__(self, chunks: list):
        self.chunks = chunks
        self.doc_freq = Counter()
        for chunk in chunks:
            for term in set(chunk.tokens):
                self.doc_freq[term] += 1
        self.vectors = [self._vectorize(chunk.tokens) for chunk in chunks]

    def _idf(self, term: str) -> float:
        n = max(len(self.chunks), 1)
        return math.log((n + 1) / (self.doc_freq.get(term, 0) + 1)) + 1.0

    def _vectorize(self, tokens: list) -> dict:
        counts = Counter(tokens)
        if not counts:
            return {}
        return {t: (c / len(tokens)) * self._idf(t) for t, c in counts.items()}

    @staticmethod
    def _cosine(a: dict, b: dict) -> float:
        if not a or not b:
            return 0.0
        dot = sum(v * b.get(t, 0.0) for t, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def search(self, query: str, top_k: int = 5, topic_boost: list = None) -> list:
        """Return [(chunk, score)] sorted by score, best first."""
        q = self._vectorize(tokenize(query))
        scored = []
        for chunk, vec in zip(self.chunks, self.vectors):
            score = self._cosine(q, vec)
            if topic_boost:
                overlap = len(set(topic_boost) & set(chunk.topics))
                score += 0.05 * overlap
            if score > 0:
                scored.append((chunk, round(score, 4)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
