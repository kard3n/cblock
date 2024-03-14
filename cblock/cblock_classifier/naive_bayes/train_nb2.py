import nltk
import numpy as np
from nltk import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB, ComplementNB
from timeit import default_timer as timer

from create_dataset import clean_dataset


nltk.download("stopwords")
nltk.download("punkt")

# stemmer = nltk.SnowballStemmer("english", ignore_stopwords=False)


print("Creating dataset...")
df = clean_dataset("../MN-DS-news-classification.csv")

# convert to lower case
df["content"] = df.content.map(lambda x: x.lower())

# remove punctuation
df["content"] = df.content.str.replace("[^\w\s]", "")

# tokenize
nltk.download("stopwords")
nltk.download("punkt")
df["content"] = df["content"].apply(nltk.word_tokenize)

# stem content
stemmer = PorterStemmer()
df["content"] = df["content"].apply(lambda x: [stemmer.stem(y) for y in x])

# Convert the list of words into space-separated strings
df["content"] = df["content"].apply(lambda x: " ".join(x))

# Create CountVectorizer
count_vect = CountVectorizer()

# Create document term matrix
counts = count_vect.fit_transform(df["content"])

# apply tf-idf
transformer = TfidfTransformer().fit(counts)
counts = transformer.transform(counts)

X_train, X_test, y_train, y_test = train_test_split(
    counts, df["topic"], test_size=0.1, random_state=69
)


print("Building Classifier")


# Model training
print("Starting training...")
model = ComplementNB()
model.fit(X_train, y_train)

print("Training finished!")

predicted = model.predict(X_test)

print(np.mean(predicted == y_test))

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
