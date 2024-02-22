from abc import ABC, abstractmethod


class DBManagerInterface(ABC):

    @abstractmethod
    def create_schema_table(self):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def insert(self, values: list[any]):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def insert_multiple(self, values: list[list[any]]):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def check_url_has_schema(self, url: str) -> bool:
        raise NotImplementedError("Not yet implemented")

    # return True if a database already exists, if not returns False
    @abstractmethod
    def has_database(self) -> bool:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def get_schema(self, url: str) -> tuple[str, str]:
        raise NotImplementedError("Not yet implemented")
