# Instance-Based Learning (k-NN)
topics: machine learning, instance based learning
source: Machine Learning - Tom Mitchell (Ch. 8), paraphrased notes

## Key points
- k-NN stores the training examples and classifies a new point by the majority label of its k nearest neighbours - learning is lazy, the work happens at query time.
- Everything rides on the distance metric and feature scaling; an unscaled large-range feature silently dominates the distance.
- Small k is noisy, large k blurs class boundaries; k is usually chosen by cross-validation.
- Prediction gets slower as the dataset grows, and irrelevant features hurt badly (curse of dimensionality).

## Probe questions
- Why does feature scaling matter so much more for k-NN than for a decision tree?
- How would you choose k for a dataset, and what goes wrong at k=1 and at k=500?
- Your k-NN model gets slower every month in production. Why, and what are your options?
