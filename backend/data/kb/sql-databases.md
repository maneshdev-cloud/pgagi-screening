# SQL Databases and Data Modelling
topics: sql, sql databases
source: Project knowledge base (practitioner notes)

## Key points
- Normalisation removes duplicated facts so an update happens in exactly one place; joins rebuild the views you need.
- Indexes trade write cost and storage for read speed - index the columns you filter and join on, not everything.
- Transactions keep multi-step writes atomic: either the whole booking lands or none of it does.
- An ORM like SQLAlchemy still generates SQL; N+1 query problems come from lazy loading inside loops, not from the ORM being slow.

## Probe questions
- How would you stop two users booking the same appointment slot at the same moment? Talk me through the database side.
- A page that lists 50 orders makes 51 database queries. What is this problem called and how do you fix it?
- When is denormalising a table the right call despite the duplication?
