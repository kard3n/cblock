from abc import ABC, abstractmethod

from db import SchemaSearchResult
from db.PathSearchResult import PathSearchResult
from db.SchemaDefinition import SchemaDefinition


class DBManagerInterface(ABC):

    @abstractmethod
    def initialize_database(self):
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def insert(self, values: list[SchemaDefinition]) -> None:
        """
        Inserts multiple schemas into the database
        :param values:
        :return:
        """
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def check_url_has_schema(self, url: str) -> bool:
        raise NotImplementedError("Not yet implemented")

    # return True if a database already exists, if not returns False
    @abstractmethod
    def has_database(self) -> bool:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def get_schema(self, schema_id: str) -> SchemaSearchResult:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def get_paths_for_url(self, url: str) -> list[PathSearchResult]:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    def close_connection(self) -> None:
        """
        Closes the connection to the database
        """
        raise NotImplementedError("Not yet implemented")
