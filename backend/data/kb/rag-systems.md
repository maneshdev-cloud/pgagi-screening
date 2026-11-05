# LLM and RAG Systems
topics: rag, llm, nlp
source: Project knowledge base (practitioner notes)

## Key points
- Retrieval-augmented generation grounds a language model: documents are chunked, embedded, retrieved by similarity to the question, and passed in as context.
- Chunking strategy decides what retrieval can find - chunks that split mid-idea retrieve badly no matter how good the embedding model is.
- Grounding is only real if the answer can be traced back to retrieved chunks; showing the sources is what makes it verifiable.
- When retrieval returns nothing relevant, the safe behaviour is to say so, not to let the model improvise an answer.

## Probe questions
- Walk me through the full path of a user question in a RAG system, from typing it to the final answer.
- Your RAG system gives confident wrong answers. Where do you look first - retrieval or generation - and how do you tell which is failing?
- Why does chunk size matter, and what breaks when chunks are too big or too small?
