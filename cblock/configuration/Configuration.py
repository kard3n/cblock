import configparser


class Configuration:
    config: configparser.ConfigParser

    def __init__(self, config_file: str = None) -> None:
        self._config_file = config_file
        self.config = configparser.ConfigParser()
        if config_file is None:
            self._config_file = "config/config.ini"
            self.config.read(self._config_file)
        else:
            self.config.read(self._config_file)

    def __getattr__(self, item):
        if item == "classifier":
            return self.config["classifier"]["Classifier"]
        if item == "proxy_host":
            return self.config["application"]["ProxyHost"]
        if item == "proxy_port":
            return self.config["application"]["ProxyPort"]
        if item == "application_url":
            return self.config["application"]["ApplicationUrl"]

    # __set_attr__ causes errors
    def set_attribute(self, key, value):
        if key == "classifier":
            self.config.set("classifier", "classifier", value)

        with open(self._config_file, "w") as configfile:
            self.config.write(configfile)

    def get_config(self) -> configparser.ConfigParser:
        """
        Returns the ConfigParser object used internally by the class
        """
        return self.config
