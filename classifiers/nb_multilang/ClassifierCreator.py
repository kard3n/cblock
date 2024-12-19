import pathlib
import time

import nltk
from cloudpickle import cloudpickle
from nltk import word_tokenize, SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline

from classifiers.nb_multilang.create_dataset import create_dataset


class ClassifierCreator:
    def stem_tokenize_string(self, string: str) -> str:
        result: [str] = []
        tokenized = word_tokenize(string)

        for word in tokenized:
            result.append(self.stemmer.stem(word))

        return result

    def create_classifier(
        self, language: str, param_grid: dict, select_k_features: int
    ) -> None:
        """

        :param language: the language that should be used
        :param param_grid:
        :param select_k_features: How many features should be selected for the model
        :return:
        """

        print("Creating classifier for language: " + language)

        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")

        # nltk.download("averaged_perceptron_tagger")

        # New languages must be added here
        language_code_to_name = {"en": "english", "de": "german"}

        self.stemmer = SnowballStemmer(
            language_code_to_name[language], ignore_stopwords=False
        )

        dataset_loc = (
            pathlib.Path(__file__).parent.resolve().as_posix()
            + "/datasets/dataset_"
            + language
            + ".csv"
        )

        categories_to_remove = ["finance", "environment_disaster", "health_drugs"]

        dataset = create_dataset(
            ds_location=dataset_loc,
            only_title=False,
            categories_to_remove=categories_to_remove,
        )

        dataset_x = dataset["content"]
        dataset_y = dataset["topic"]

        x_train, x_test, y_train, y_test = train_test_split(
            dataset_x, dataset_y, test_size=0.25, random_state=50, stratify=dataset_y
        )

        cv = CountVectorizer(
            # TODO: create stopword list for each language
            # stop_words=language, # Doesn't accept values other than list, None or english
            tokenizer=self.stem_tokenize_string,
            strip_accents="unicode",
            lowercase=True,
        )

        # chi2, f_classif, mutual_info_classif
        skb = SelectKBest(score_func=mutual_info_classif, k=select_k_features)

        x_train_vectorized = cv.fit_transform(x_train)

        x_train_ig = skb.fit_transform(X=x_train_vectorized, y=y_train)

        new_features = skb.get_feature_names_out(
            input_features=cv.get_feature_names_out()
        )

        # Cross Validation

        pipeline_cv = make_pipeline(ComplementNB())
        grid_search = GridSearchCV(
            pipeline_cv,
            param_grid=param_grid,
            return_train_score=True,
            cv=10,
            verbose=2,
            n_jobs=-1,
            scoring="f1_macro",
        )

        grid_search.fit(x_train_ig, y_train)

        print("Best parameters: ", grid_search.best_params_)

        cnb = grid_search.best_estimator_

        pipeline = make_pipeline(
            CountVectorizer(
                # TODO: create stopword list for each language
                # stop_words=language,
                tokenizer=self.stem_tokenize_string,
                strip_accents="unicode",
                vocabulary=new_features,
            ),
            cnb,
        )
        y_pred = pipeline.predict(x_test)

        num_tests = 10
        test_start_time = time.time()
        for i in range(num_tests):
            pipeline.predict(x_test)
        test_end_time = time.time()

        feature_dict_test = {}
        for item in y_test:
            if item not in feature_dict_test.keys():
                feature_dict_test[item] = 1
            else:
                feature_dict_test[item] += 1

        feature_dict_train = {}
        for item in y_train:
            if item not in feature_dict_train.keys():
                feature_dict_train[item] = 1
            else:
                feature_dict_train[item] += 1

        print("Features in test dataset: ", feature_dict_test)
        print("Features in train dataset: ", feature_dict_train)

        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("F1 score:", f1_score(y_test, y_pred, average="macro"))
        print("Recall score: ", recall_score(y_test, y_pred, average="weighted"))
        print("Number of features: ", cnb.n_features_in_)
        print(
            f"Time required to classify {y_pred.shape[0] * num_tests} instances: {test_end_time - test_start_time}s"
        )

        cloudpickle.dump(pipeline, open("classifier_" + language + ".pickle", "wb"))
