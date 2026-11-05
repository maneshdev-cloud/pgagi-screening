# Python APIs with FastAPI
topics: fastapi, python, rest api
source: Project knowledge base (practitioner notes)

## Key points
- FastAPI builds on Starlette and Pydantic: request/response shapes are declared as models and validated automatically, which catches bad input at the edge.
- Dependency injection (Depends) is how database sessions, auth and shared config reach route handlers without globals.
- Async endpoints help when handlers wait on I/O; CPU-heavy work in an async handler still blocks the event loop and belongs in a worker or a plain def endpoint.
- Validation errors return 422 with a useful body - clients should never have to guess which field failed.

## Probe questions
- What does Pydantic validation buy you in FastAPI, and what happens when a request body fails it?
- When would you make an endpoint async def versus plain def, and what goes wrong if you mix them up with a blocking call?
- How would you share one database session per request across routes without creating it inside every handler?
