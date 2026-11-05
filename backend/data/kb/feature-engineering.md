# Feature Engineering and Data Preprocessing
topics: machine learning, data analysis
source: Project knowledge base (practitioner notes)

## Key points
- Models eat numbers: categorical values need encoding (one-hot, ordinal, target), and the choice changes what the model can learn.
- Missing values are information, not just holes - the fact that a field is empty often correlates with the target.
- Scaling matters for distance- and gradient-based models; tree models mostly do not care.
- Leakage is the silent killer: any feature computed using future information (or the target itself) inflates offline scores and dies in production.

## Probe questions
- Give me an example of target leakage you have seen or could imagine, and how you would catch it.
- When would one-hot encoding hurt you, and what would you use instead for a high-cardinality column?
- A column is 40% missing. What are your options, and how do you decide?
