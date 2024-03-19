import nltk
from pandas import DataFrame

stemmer = nltk.SnowballStemmer("english", ignore_stopwords=False)


def stem_tokenize_string(string: str):
    result: str = ""
    tokenized = nltk.word_tokenize(string)
    for word in tokenized:
        result += stemmer.stem(word) + " "
    return result.split()


def stem_string(string: str) -> str:
    result: str = ""
    for word in string.split():
        result += stemmer.stem(word) + " "
    return result


def stem_dataset_column(dataset: DataFrame, column_name: str) -> DataFrame:
    for i, row in dataset.iterrows():
        dataset.at[i, column_name] = stem_tokenize_string(row[column_name])

    return dataset
