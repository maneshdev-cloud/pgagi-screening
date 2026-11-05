# Decision Trees
topics: machine learning, decision trees
source: Machine Learning - Tom Mitchell (Ch. 3), paraphrased notes

## Key points
- A decision tree sorts examples down from the root, testing one attribute per node, until a leaf gives the class.
- ID3 picks the attribute with the highest information gain - the split that reduces entropy of the labels the most.
- Deep trees memorise noise, so pruning or depth limits matter; a tree that fits every training point usually generalises worse.
- Trees handle mixed feature types and are easy to explain, but small data changes can produce a very different tree (high variance).

## Probe questions
- In your own words, what is information gain actually measuring when a tree chooses a split?
- Why does a fully grown decision tree tend to overfit, and what are two ways to control that?
- A tree changes completely when you remove 5% of the training rows. What does that tell you, and what could stabilise it?
