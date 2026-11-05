# React and Next.js Frontends
topics: react, next.js, javascript, typescript
source: Project knowledge base (practitioner notes)

## Key points
- React renders UI as a function of state; when state changes, the affected components re-render - side effects belong in effects or event handlers, not in render.
- Next.js adds file-based routing and server rendering: pages can be rendered on the server for first paint and SEO, then hydrated on the client.
- Client components cannot keep secrets - anything shipped to the browser, including API keys in env vars prefixed for the client, is public.
- Keys in lists are how React tracks identity between renders; using array indexes as keys causes subtle bugs when items reorder.

## Probe questions
- What actually happens in React when you call a state setter - walk me through the re-render.
- Why would you render a page on the server with Next.js instead of purely on the client? What do you gain and lose?
- A list in your UI scrambles its row state whenever an item is deleted. What is the likely cause?
