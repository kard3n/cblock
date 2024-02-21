from abc import ABC, abstractmethod


class DBManagerInterface(ABC):

    @abstractmethod
    def create_schema_table(self):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def insert(self, table_name: str, values: list[any]):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def insert_multiple(self, table_name: str, values: list[list[any]]):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def check_url_has_schema(self, url: str) -> bool:
        raise NotImplementedError("Not yet implemented")
