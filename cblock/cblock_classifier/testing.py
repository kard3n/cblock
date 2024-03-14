import nltk
from nltk import SnowballStemmer, word_tokenize

nltk.download("stopwords")
nltk.download("punkt")

stemmer = SnowballStemmer("english", ignore_stopwords=True)


def stem_string(string: str):
    result: str = ""
    tokenized = word_tokenize(string)
    for word in tokenized:
        result += stemmer.stem(word) + " "
    return result


print(stem_string("Hi there, you guys are idiots. now leave!"))
