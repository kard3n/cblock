import json
import os
import sys
import traceback
from importlib import import_module

from content_classifier.ClassifierInfo import ClassifierInfo
from content_classifier.ContentClassifierInterface import ContentClassifierInterface


class ClassifierManager:
    def __init__(self, classifier_directory: str):
        self._classifier_directory = classifier_directory
        self._classifiers = {}
        self._classifier_info = {}

        dir_list = os.listdir(classifier_directory)

        print(f"Initializing classifiers from {self._classifier_directory}")

        # Adds path of the executable to PYTHONPATH, so that python can find modules in it
        # Needed for usage with pyinstaller
        sys.path.append(os.path.dirname(sys.executable))

        for obj in dir_list:
            path = self._classifier_directory + "/" + obj

            if os.path.isdir(path) and not path.endswith("__pycache__"):
                try:
                    info = ClassifierInfo.from_dict(
                        json.load(open(path + "/info.json", "rt"))
                    )
                    info.directory_path = path

                    if (
                        info.name in self._classifiers.keys()
                    ):  # Check that no name exists twice
                        print(
                            f"\tWarning: classifier {info.name} has already been registered. Ignoring."
                        )
                    else:

                        module = import_module(f"classifiers.{obj}.{info.filename}")

                        self._classifiers[info.name] = getattr(module, "classifier")(
                            topics_to_remove=info.topic_blacklist,
                            aggressiveness=info.aggressiveness,
                        )

                        self._classifier_info[info.name] = info

                        print(
                            f"\tLoaded classifier '{info.nickname}': classifiers.{obj}"
                        )

                except Exception as e:
                    print(
                        f'\tError importing classifier from directory "{obj}": {traceback.format_exc()}'
                    )

    @property
    def classifier_info(self) -> dict:
        return self._classifier_info

    def get_classifier(self, name: str) -> ContentClassifierInterface:
        return self._classifiers[name]

    def set_aggressiveness(self, classifier_name: str, aggressiveness: float):
        """
        Sets the aggressiveness of the classifier with the given name. Updates its info.json automatically.
        :param classifier_name:
        :param aggressiveness:
        :return:
        """
        self._classifier_info[classifier_name].aggressiveness = aggressiveness
        self._classifiers[classifier_name].set_aggressiveness(aggressiveness)

        self._save_settings(classifier_name=classifier_name)

    def set_topic_blacklist(self, classifier_name: str, topic_blacklist: list[str]):
        """
        Sets the topic blacklist of the classifier with the given name. Updates its info.json automatically.
        :param classifier_name:
        :param topic_blacklist:
        :return:
        """
        self._classifier_info[classifier_name].topic_blacklist = []
        # make sure only valid topics can be added
        for topic in topic_blacklist:
            if topic in self._classifiers[classifier_name].get_supported_topics():
                self._classifier_info[classifier_name].topic_blacklist.append(topic)
            else:
                print("Can not in-existing topic: " + topic)
        self._classifiers[classifier_name].set_topic_blacklist(topic_blacklist)

        self._save_settings(classifier_name=classifier_name)

    def _save_settings(self, classifier_name: str):
        json.dump(
            obj=self._classifier_info[classifier_name].to_dict(),
            fp=open(
                os.path.join(
                    self._classifier_info[classifier_name].directory_path, "info.json"
                ),
                "wt",
            ),
            indent=4,
        )
