# Supervised Learning Basics
topics: machine learning, supervised learning
source: Machine Learning - Tom Mitchell (Ch. 1-2), paraphrased notes

## Key points
- Supervised learning trains a function from labelled examples: inputs paired with the target output we want to predict.
- The learned hypothesis is judged on unseen data, not the training set - generalisation is the whole point.
- Mitchell frames it as choosing a hypothesis consistent with the training examples, then preferring simpler ones (a form of inductive bias).
- Classification predicts discrete labels, regression predicts continuous values; mixing them up leads to the wrong loss and metrics.

## Probe questions
- If a model scores 99% on training data but 70% on new data, what has gone wrong and what would you check first?
- How do you decide whether a problem should be framed as classification or regression? Give an example of each.
- What does inductive bias mean in practice when you pick one model family over another?
