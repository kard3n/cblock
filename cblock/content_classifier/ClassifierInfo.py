class ClassifierInfo:
    """
    Saves information about the classifier and its settings such as its topic blacklist and aggressiveness
    """

    def __init__(
        self, name, nickname, filename, description, topic_blacklist, aggressiveness
    ):
        self._name: str = name
        self._nickname: str = nickname
        self._filename: str = filename
        self._description: str = description
        self._topic_blacklist: list[str] = topic_blacklist
        self._aggressiveness: float = aggressiveness

    @property
    def name(self) -> str:
        return self._name

    @property
    def nickname(self) -> str:
        return self._nickname

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def description(self) -> str:
        return self._description

    @property
    def topic_blacklist(self) -> list[str]:
        return self._topic_blacklist

    @topic_blacklist.setter
    def topic_blacklist(self, value: list[str]) -> None:
        self._topic_blacklist = value

    @property
    def aggressiveness(self) -> float:
        return self._aggressiveness

    @aggressiveness.setter
    def aggressiveness(self, value: float) -> None:
        self._aggressiveness = value

    @property
    def directory_path(self) -> str:
        return self._directory_path

    @directory_path.setter
    def directory_path(self, value: str) -> None:
        self._directory_path = value

    @staticmethod
    def from_dict(d: dict):
        return ClassifierInfo(
            d["name"],
            d["nickname"],
            d["filename"],
            d["description"],
            d["topic_blacklist"],
            d["aggressiveness"],
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "nickname": self.nickname,
            "filename": self.filename,
            "description": self.description,
            "topic_blacklist": self.topic_blacklist,
            "aggressiveness": self.aggressiveness,
        }
