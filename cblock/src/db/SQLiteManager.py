import sqlite3

from src.db.DBManagerInterface import DBManagerInterface


class SQLiteManager(DBManagerInterface):
    connection: sqlite3.Connection
    database_name: str
    cursor: sqlite3.Cursor
    table_name: str

    def __init__(self, database_name: str, table_name: str) -> None:
        self.database_name = database_name
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()
        self.table_name = table_name

    def create_schema_table(self) -> None:
        self.create_table(
            id_column="schema_id",
            non_id_columns=["name", "url", "schema_type", "schema"],
            columns_to_index=["url"],
        )

    # Creates a table. If it already exists, overwrites it
    def __create_table(
        self,
        id_column: str | None,
        non_id_columns: list[str],
        columns_to_index: list[str] | None = None,
    ):
        create_sentence: str = (
            f"CREATE TABLE {self.table_name}({self.__columns_to_comma_separated(id_column=id_column, columns=non_id_columns)})"
        )

        # Check if the 'table_name' table exists
        # TODO maybe improve queries
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.table_name}'"
            ).fetchone()
            is not None
        ):
            self.cursor.execute(f"DROP TABLE {self.table_name}")

        # Create fresh table
        if id_column is not None:
            self.cursor.execute(create_sentence + "WITHOUT ROWID")
        else:
            self.cursor.execute(create_sentence)

        for index in columns_to_index:
            self.cursor.execute(
                f"CREATE INDEX {index}_index ON {self.table_name}({index})"
            )

        self.connection.commit()

    def __columns_to_comma_separated(self, id_column: str | None, columns: list[str]):
        res: str = ""
        if id_column is not None:
            res += id_column + " NOT NULL PRIMARY KEY,"

        for column in columns:
            res += column + ","

        return res[:-1]

    def insert(self, table_name: str, values: list[any]):
        self.cursor.execute(
            f"INSERT INTO {table_name} VALUES ({self.__list_to_comma_separated(values)}"
        )
        self.connection.commit()

    def insert_multiple(self, table_name: str, values: list[list[any]]):
        for value in values:
            self.cursor.execute(
                f"INSERT INTO {table_name} VALUES ({self.__list_to_comma_separated(value)}"
            )

        self.connection.commit()

    def __list_to_comma_separated(self, items: list[str]):
        res: str = ""
        for item in items:
            res += item + ","

        return res[:-1]

    def check_url_has_schema(self, url: str) -> bool:
        if (
            self.cursor.execute(f"SELECT url FROM  WHERE url = '{url}'").fetchone()
            is not None
        ):
            return True
        return False
