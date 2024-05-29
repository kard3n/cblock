import configparser


class Configuration:
    config: configparser.ConfigParser

    def __init__(self, config_file: str = None) -> None:
        self.config = configparser.ConfigParser()
        if config_file is None:
            self.config.read("config/config.ini")
        else:
            self.config.read(config_file)

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
