import datetime
import logging
import os.path
import pathlib

from content_classifier.ContentClassifierInterface import ContentClassifierInterface
from editor.ContentExtractionResult import ContentExtractionResult


class ContentToFileClassifier(ContentClassifierInterface):
    def __init__(self):
        if not os.path.isdir("extracted_headlines"):
            os.mkdir("extracted_headlines")

    def classify(self, content: ContentExtractionResult) -> bool:
        if content.title != "":
            with open(
                r"extracted_headlines/"
                + datetime.date.today().strftime("%Y_%m_%d")
                + ".csv",
                "at",
                encoding="utf-8",
            ) as file:
                file.write(
                    f'""", {content.title.replace('"', r'""')}", "{content.text.replace('"', r'""')}",""\n'
                )
                logging.warning(os.path.abspath(file.name))

        return True
