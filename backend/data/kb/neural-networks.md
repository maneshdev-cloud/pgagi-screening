# Neural Networks and Backpropagation
topics: machine learning, neural networks, deep learning
source: Machine Learning - Tom Mitchell (Ch. 4), paraphrased notes

## Key points
- A neural network composes weighted sums with non-linear activations; without the non-linearity the whole stack collapses into one linear function.
- Backpropagation applies the chain rule to push the loss gradient back through the layers so each weight gets its share of the blame.
- Gradient descent can stall in local minima or plateaus, which is why initialisation, learning rate and momentum matter.
- Networks need more data and tuning than simpler models, and they overfit happily unless regularised or stopped early.

## Probe questions
- Why does a network with only linear activations fail on problems a single hidden layer should solve?
- Walk me through what backpropagation computes, step by step, for one training example.
- Your training loss stopped improving in the first epoch. What are the first three things you would inspect?
