import nltk
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB, ComplementNB
from timeit import default_timer as timer

from create_dataset import clean_dataset


nltk.download("stopwords")
nltk.download("punkt")

stemmer = nltk.SnowballStemmer("english", ignore_stopwords=False)


def stem_string(string: str):
    result: str = ""
    tokenized = nltk.word_tokenize(string)
    for word in tokenized:
        result += stemmer.stem(word) + " "
    return result


print("Creating dataset...")
dataset = clean_dataset("../MN-DS-news-classification.csv")

# stem values of content column
"""for i, row in dataset.iterrows():
    dataset.at[i, "content"] = stem_string(row["content"])"""

dataset_X = dataset["content"]
dataset_y = dataset["topic"]


# TODO maybe use TF-IDF to remove words of low interest
count_vectorizer = CountVectorizer(
    stop_words="english",
    strip_accents="unicode",
    lowercase=True,
    analyzer="word",
    # max_df=0.20,  # if a word appears in more than max_df*100% of the documents, it is not used
    # min_df=0.0004,  # if a word appears in less than min_df*100% of the documents, it is not used
    # max_features=None,  # setting this to an int (ex: 50000) highly reduces testing/prediction time but may reduce accuracy. Default: None
)


print("Vectorizing dataset...")
bow = count_vectorizer.fit_transform(dataset_X)
bow = np.array(bow.todense())


X_train, X_test, y_train, y_test = train_test_split(
    bow, dataset_y, test_size=0.3, random_state=100, stratify=dataset_y
)

print("Building Classifier")
# Build a Gaussian Classifier
model = ComplementNB()

# Model training
print("Starting training...")
model.fit(X_train, y_train)
print("Training finished!")


print("Testing...")
# Test result
start = timer()
# test 10 times
for i in range(0, 10):
    y_pred = model.predict(X_test)
end = timer()
print("Testing finished!")

print("Testing dataset shape: {}".format(X_test.shape))


print("Accuracy:", accuracy_score(y_test, y_pred))
print("F1 score:", f1_score(y_test, y_pred, average="macro"))
print(f"Time required for testing: {end - start}")
