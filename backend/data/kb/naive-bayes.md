# Naive Bayes and Probabilistic Learning
topics: machine learning, naive bayes, nlp, statistics
source: Machine Learning - Tom Mitchell (Ch. 6), paraphrased notes

## Key points
- Bayes rule turns a prior belief plus observed evidence into a posterior probability for each class.
- Naive Bayes assumes features are independent given the class - usually false, yet the classifier still ranks classes well surprisingly often.
- Zero counts break the maths, so Laplace (add-one) smoothing is used to keep unseen word/feature combinations possible.
- It is a strong, fast baseline for text classification because word counts fit its assumptions well enough.

## Probe questions
- What exactly is "naive" about Naive Bayes, and why does it still work well for text classification?
- A word in a test email never appeared in training. What breaks, and how does smoothing fix it?
- When would you pick Naive Bayes over a neural network for a classification job?
