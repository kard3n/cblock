import os
import sys

sys.path.append(os.getcwd())

from classifiers.nb_multilang.create_language_classifier import create_language_classifier
from classifiers.nb_multilang.create_classifier import create_classifier

lang_to_param_grid: dict = {
    "en": {
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
    },
    "de": {
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
    },
}

lang_to_k_features: dict = {"en": 5500, "de": 2000}

languages: list[str] = ["en", "de"]

# Create classifiers for the different languages
for lang in languages:
    create_classifier(
        language=lang,
        param_grid=lang_to_param_grid[lang],
        select_k_features=lang_to_k_features[lang],
    )

# Create a classifier for language detection

create_language_classifier(
    languages=languages, select_k_features_per_language=20
)
