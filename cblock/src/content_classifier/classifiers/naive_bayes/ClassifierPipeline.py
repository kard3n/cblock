from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline, Pipeline
from timeit import default_timer as timer
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
import nltk

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

from content_classifier.classifiers.naive_bayes.utils.utils import (
    stem_string,
)


class ClassifierPipeline:
    def __init__(self, stem_input: bool = True, stem_tokens: bool = False):
        """

        :param stem_input: If True, the input is stemmed before being applied NER
        :param stem_tokens: If True, the result is stemmed after applying NER
        """
        self.stem_tokens = stem_tokens
        self.stem_input = stem_input
        self.__model: Pipeline | None = None
        nltk.download("averaged_perceptron_tagger")

    def train(self, x, y):

        print("Building Classifier")
        # Build a Naive Bayes Classifier
        # Options:
        #   preprocessor=stem_string
        #   tokenizer=stem_tokenize_string
        #   analyzer='word' (default)
        model = make_pipeline(
            CountVectorizer(preprocessor=self.preprocess), ComplementNB()
        )

        # Model training
        print("Starting training...")
        model.fit(x, y)
        print("Training finished!")

        self.__model = model

    def predict(self, string: str):
        return self.__model.predict([string])

    def predict_proba(self, string: str):
        return self.__model.predict_proba([string])

    def test_training(self, x, y):
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.3, random_state=50, stratify=y
        )

        self.train(x_train, y_train)

        print("Testing...")
        start = timer()
        y_pred = self.__model.predict(x_test)
        end = timer()
        print(f"Testing finished in {end - start} seconds.")

        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("F1 score:", f1_score(y_test, y_pred, average="macro"))

        ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
        plt.show()

    def preprocess(self, input_str: str):

        if self.stem_input:
            result: str = stem_string(input_str)
        else:
            result = input_str
        result = "".join(
            [
                x[0] + " " if x[1] in ["NN", "NNP", "VBZ", "JJ"] else ""
                for x in pos_tag(word_tokenize(result))
            ]
        )

        if self.stem_tokens:
            return stem_string(result)
        else:
            return result
