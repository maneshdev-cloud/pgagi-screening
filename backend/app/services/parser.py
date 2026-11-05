"""Resume parsing: pull text out of an upload, then extract a simple
structured profile (skills, technologies, domain exposure).

The extraction is dictionary based on purpose - it is predictable, easy to
extend, and easy to test. It is not trying to be a full NLP pipeline.
"""
import io
import re

# canonical skill -> aliases that show up in resumes
SKILL_ALIASES = {
    "python": ["python"],
    "machine learning": ["machine learning", "ml models", "ml pipelines"],
    "deep learning": ["deep learning", "neural networks", "neural network"],
    "tensorflow": ["tensorflow"],
    "keras": ["keras"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "nlp": ["nlp", "natural language processing", "text classification"],
    "computer vision": ["computer vision", "image classification", "object detection", "cnn"],
    "data analysis": ["data analysis", "data analytics", "eda", "exploratory data"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "rest api": ["rest api", "restful", "api development", "apis"],
    "react": ["react", "react.js", "reactjs"],
    "next.js": ["next.js", "nextjs"],
    "javascript": ["javascript"],
    "typescript": ["typescript"],
    "node.js": ["node.js", "nodejs", "express"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "rag": ["rag", "retrieval augmented", "retrieval-augmented", "langchain", "embeddings", "vector database"],
    "llm": ["llm", "large language model", "gpt", "gemini", "groq", "prompt engineering"],
    "statistics": ["statistics", "statistical", "probability"],
    "data structures": ["data structures", "algorithms", "dsa"],
    "cloud deployment": ["vercel", "netlify", "aws", "gcp", "cloudflare", "render"],
    "testing": ["testing", "pytest", "vitest", "unit tests", "automated tests"],
    "supabase": ["supabase", "firebase"],
}

# rough split: "skills" are concepts, "technologies" are tools/frameworks.
TECHNOLOGIES = {
    "tensorflow", "keras", "pytorch", "scikit-learn", "sql", "fastapi", "flask",
    "react", "next.js", "javascript", "typescript", "node.js", "git", "docker",
    "supabase",
}

# domain exposure: what kind of problems has this person touched?
DOMAIN_KEYWORDS = {
    "healthcare": ["clinic", "patient", "doctor", "healthcare", "medical", "hospital"],
    "finance": ["finance", "banking", "payment", "merchant", "trading", "fintech"],
    "e-commerce": ["e-commerce", "ecommerce", "shop", "store", "restaurant", "food delivery"],
    "education": ["education", "student", "course", "learning platform"],
    "nlp / text": ["chatbot", "sentiment", "summarisation", "summarization", "assistant"],
    "operations / scheduling": ["scheduling", "roster", "queue", "booking", "appointment"],
}


def extract_text_from_upload(filename: str, data: bytes) -> str:
    """PDFs go through pypdf; everything else is treated as plain text."""
    if filename.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    return data.decode("utf-8", errors="ignore").strip()


def _find_terms(text: str, mapping: dict) -> list:
    low = text.lower()
    found = []
    for canonical, aliases in mapping.items():
        for alias in aliases:
            if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", low):
                found.append(canonical)
                break
    return found


def parse_resume(text: str) -> dict:
    skills = _find_terms(text, SKILL_ALIASES)
    technologies = [s for s in skills if s in TECHNOLOGIES]
    concepts = [s for s in skills if s not in TECHNOLOGIES]
    domains = _find_terms(text, DOMAIN_KEYWORDS)

    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    return {
        "skills": concepts,
        "technologies": technologies,
        "all_skills": skills,
        "domains": domains,
        "email": email.group(0) if email else "",
        "word_count": len(text.split()),
    }
