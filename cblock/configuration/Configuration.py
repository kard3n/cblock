import configparser


class Configuration:
    config: configparser.ConfigParser

    def __init__(self, config_file: str = None) -> None:
        self.config = configparser.ConfigParser()
        if config_file is None:
            self.config.read("config/config.ini")
        else:
            self.config.read(config_file)

    def get_topics_to_remove(self) -> list[str]:
        """
        Returns the list of topics recovered from the configuration file
        :return: (list[str]): List of topics
        """
        found_topics: list = self.config.get("basic", "TopicsToRemove").split("\n")
        for item in found_topics:
            if not item.strip():
                found_topics.remove(item)

        return found_topics

    def __getattr__(self, item):
        if item == "classifier":
            return self.config["classifier"]["ClassifierToUse"]
        if item == "proxy_host":
            return self.config["application"]["ProxyHost"]
        if item == "proxy_port":
            return self.config["application"]["ProxyPort"]

    def get_config(self) -> configparser.ConfigParser:
        """
        Returns the ConfigParser object used internally by the class
        """
        return self.config
