import pathlib
import time

from cloudpickle import cloudpickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline
import pandas
from pandas import DataFrame


class LanguageClassifierCreator:
    def create_dataset(
        self,
        languages: list[str],
        only_title: bool = False,
    ) -> DataFrame:

        combined_df = None

        for lang in languages:
            ds_location = (
                pathlib.Path(__file__).parent.resolve().as_posix()
                + "/datasets/dataset_"
                + lang
                + ".csv"
            )
            current_lang_df = pandas.read_csv(ds_location)
            current_lang_df["label"] = lang
            if combined_df is None:
                combined_df = current_lang_df.copy()
            else:
                combined_df = pandas.concat(
                    [combined_df, current_lang_df], ignore_index=True
                )

        data = {"content": [], "topic": []}
        if only_title:
            for index, row in combined_df.iterrows():
                data["content"].append(row["title"])
                data["topic"].append(row["label"])
        else:
            for index, row in combined_df.iterrows():
                data["content"].append(
                    row["title"]
                    + " "
                    + (row["text"] if type(row["text"]) is str else "")
                )
                data["topic"].append(row["label"])

        result: DataFrame = DataFrame(data)

        return result

    def create_classifier(
        self, languages: list[str], select_k_features_per_language: int
    ) -> None:
        """
        :param languages: the languages that the classifier should be able to detect
        :param select_k_features_per_language: How many features should be selected for the model
        :return:
        """

        print("Creating language classifier")

        param_grid = {
            "complementnb__alpha": [
                0.35,
                0.5,
                0.85,
                1.0,
                1.1,
                1.2,
                1.3,
                1.4,
                1.47,
                1.5,
                1.6,
                1.7,
                2.0,
                3.0,
            ],
            "complementnb__fit_prior": [True, False],
            "complementnb__norm": [True, False],
        }

        dataset = self.create_dataset(only_title=False, languages=languages)

        dataset_x = dataset["content"]
        dataset_y = dataset["topic"]

        x_train, x_test, y_train, y_test = train_test_split(
            dataset_x, dataset_y, test_size=0.25, random_state=50, stratify=dataset_y
        )

        cv = CountVectorizer(
            strip_accents="unicode",
            lowercase=True,
        )

        # chi2, f_classif, mutual_info_classif
        skb = SelectKBest(
            score_func=mutual_info_classif,
            k=select_k_features_per_language * languages.__len__(),
        )

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

        cloudpickle.dump(pipeline, open("language_classifier.pickle", "wb"))
