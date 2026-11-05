# Model Evaluation and Overfitting
topics: machine learning, model evaluation, statistics
source: Machine Learning - Tom Mitchell (Ch. 5), paraphrased notes

## Key points
- Hold out a test set the model never trains on; tuning on the test set quietly turns it into training data.
- Cross-validation rotates which fold is held out, giving a less lucky-or-unlucky estimate than a single split.
- Overfitting means the hypothesis fits training quirks that do not repeat; more data, simpler models and regularisation all push back.
- Accuracy alone misleads on imbalanced data - a model that always predicts the majority class can look great and be useless.

## Probe questions
- Why is it a problem to keep tuning a model against the same test set until the score looks good?
- How does k-fold cross-validation give a more honest estimate than one train/test split?
- A fraud model reports 99.2% accuracy but catches almost no fraud. What is happening and which metrics would you look at instead?
