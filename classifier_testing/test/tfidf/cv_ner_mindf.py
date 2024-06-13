import pathlib
import time

import joblib
from cloudpickle import cloudpickle
from nltk import pos_tag, word_tokenize, SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2, mutual_info_classif, f_classif
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline

from classifier_scripts.create_dataset import create_dataset

stemmer = SnowballStemmer("english", ignore_stopwords=False)


def stem_tokenize_string(string: str):
    result: [str] = []
    tokenized = word_tokenize(string)

    for word in tokenized:
        result.append(stemmer.stem(word))

    return result


def ner(input_str: str):
    input_str = "".join(
        [
            (
                x[0] + " "
                if x[1]
                in [
                    "NN",
                    "NNP",
                    "NNS",
                    "VBD",
                    "VBG",
                    "VBN",
                    "VBP",
                    "VBZ",
                    "VB",
                    "JJ",
                ]
                else ""
            )
            for x in pos_tag(word_tokenize(input_str))
        ]
    )
    return input_str


dataset_loc = pathlib.Path(__file__).parent.resolve().as_posix() + "/test_v2_7.csv"

categories_to_remove = ["finance", "environment_disaster", "health_drugs"]

dataset = create_dataset(
    ds_location=dataset_loc, only_title=False, categories_to_remove=categories_to_remove
)

dataset_x = dataset["content"]
dataset_y = dataset["topic"]

x_train, x_test, y_train, y_test = train_test_split(
    dataset_x, dataset_y, test_size=0.25, random_state=50, stratify=dataset_y
)

# Cross Validation
param_grid = {
    "complementnb__alpha": [
        0.5,
        0.75,
        1.0,
        1.25,
        1.7,
        2.0,
        3.0,
    ],
    "complementnb__fit_prior": [True, False],
    "complementnb__norm": [True, False],
}
pipeline = make_pipeline(
    TfidfVectorizer(
        stop_words="english",
        tokenizer=stem_tokenize_string,
        strip_accents="unicode",
        lowercase=True,
        norm="l2",
        use_idf=True,
        sublinear_tf=True,
        smooth_idf=True,
        min_df=2,
    ),
    ComplementNB(),
)

grid_search = GridSearchCV(
    pipeline,
    param_grid=param_grid,
    return_train_score=True,
    cv=10,
    verbose=2,
    n_jobs=-1,
    scoring="f1_macro",
)

# apply ner
x_train_new = [ner(item) for item in x_train]

grid_search.fit(x_train_new, y_train)

print("Best parameters: ", grid_search.best_params_)

cnb = grid_search.best_estimator_

y_pred = cnb.predict(x_test)

num_tests = 10
test_start_time = time.time()
for i in range(num_tests):
    """for item in x_test:
    pipeline.predict([item])"""
    cnb.predict(x_test)
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
print("Recall score: ", recall_score(y_test, y_pred, average="micro"))
print("Number of features: ", cnb[1].n_features_in_)
print(
    f"Time required to classify {y_pred.shape[0] * num_tests} instances: {test_end_time - test_start_time}s"
)

cloudpickle.dump(pipeline, open("../classifier.pickle", "wb"))
