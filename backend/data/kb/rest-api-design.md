# REST API Design
topics: rest api, fastapi, node.js
source: Project knowledge base (practitioner notes)

## Key points
- Resources are nouns, HTTP verbs carry the action; status codes are part of the contract (201 for created, 404 for missing, 422 for invalid input).
- Stateless requests scale because any server can handle any call - session state belongs in a token or a store, not in process memory.
- Pagination, filtering and consistent error shapes matter more to clients than clever URL schemes.
- Versioning (in the path or a header) lets the API change without breaking existing clients overnight.

## Probe questions
- A client says your API "sometimes returns a list, sometimes an object, and errors look different every time". What do you standardise first?
- Why does statelessness matter when you scale from one server to three?
- When would you return 422 instead of 400 or 404? Give one concrete case for each.
