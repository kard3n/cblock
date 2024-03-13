import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB

from create_dataset import clean_dataset


print("Creating dataset...")
dataset = clean_dataset("../MN-DS-news-classification.csv")

dataset_X = dataset["content"]
dataset_y = dataset["topic"]

count_vectorizer = CountVectorizer()
print("Vectorizing dataset...")
bow = count_vectorizer.fit_transform(dataset_X)
bow = np.array(bow.todense())


X_train, X_test, y_train, y_test = train_test_split(
    bow, dataset_y, test_size=0.33, random_state=100, stratify=dataset_y
)

print("Building Classifier")
# Build a Gaussian Classifier
model = GaussianNB(verbose=1)

# Model training
print("Starting training...")
model.fit(X_train, y_train)
print("Training finished!")


print("Testing...")
# Test result
y_pred = model.predict(X_test)
print("Testing finished!")


print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1 score:", f1_score(y_test, y_pred, average="macro"))
