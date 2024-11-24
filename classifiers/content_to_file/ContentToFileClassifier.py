import datetime
import logging
import os.path


class ContentToFileClassifier:
    def __init__(self, topics_to_remove: list[str], aggressiveness: float):
        if not os.path.isdir("extracted_headlines"):
            os.mkdir("extracted_headlines")

    def classify(self, content) -> bool:
        if content.title != "":
            with open(
                r"extracted_headlines/"
                + datetime.date.today().strftime("%Y_%m_%d")
                + ".csv",
                "at",
                encoding="utf-8",
            ) as file:
                file.write(
                    '"","{title}","{text}"\n'.format(
                        title=content.title.replace('"', r'""'),
                        text=content.text.replace('"', r'""'),
                    )
                )
                logging.warning(os.path.abspath(file.name))

        return True

    def get_supported_topics(self) -> list[str]:
        return []

    def set_topic_blacklist(self, topics: list[str]):
        pass

    def set_aggressiveness(self, aggressiveness: float):
        pass

    def get_aggressiveness(self) -> float:
        return 1.0


classifier = ContentToFileClassifier
