import pickle
import sqlite3

from db.DBManagerInterface import DBManagerInterface
from db.SchemaSearchResult import SchemaSearchResult

from db.PathSearchResult import PathSearchResult


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

    # return True if a database already exists, if not returns False
    def has_database(self) -> bool:
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.table_name}'"
            ).fetchone()
            is None
        ):
            return False
        return True

    def create_schema_table(self) -> None:
        """
        Creates the schema table, and resets it if it already exists
        :return:
        """
        columns_to_index = ["url"]

        create_sentence: str = (
            f"CREATE TABLE {self.table_name}(schema_id NOT NULL PRIMARY KEY, url TEXT NOT NULL, path TEXT NOT NULL, schema_type TEXT NOT NULL, pickled_schema BLOB NOT NULL) WITHOUT ROWID"
        )

        # Check if the 'table_name' table exists, if so drops it
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.table_name}'"
            ).fetchone()
            is not None
        ):
            self.cursor.execute(f"DROP TABLE {self.table_name}")

        # Create fresh table
        self.cursor.execute(create_sentence)

        # Add indexes
        for index in columns_to_index:
            self.cursor.execute(
                f"CREATE INDEX {index}_index ON {self.table_name}({index})"
            )

        # Commit transaction
        self.connection.commit()

    def make_query_parameter_question_marks(self, num_params: int) -> str:
        question_marks = "?"
        for i in range(num_params - 1):
            question_marks += ",?"
        return question_marks

    def insert(self, values: list[any]):
        self.cursor.execute(
            f"INSERT INTO {self.table_name} VALUES ({self.make_query_parameter_question_marks(num_params=len(values))})"
        )
        self.connection.commit()

    def insert_multiple(self, values: list[list[any]]):

        for value in values:

            query = f"INSERT INTO {self.table_name} VALUES ({self.make_query_parameter_question_marks(num_params=len(value))})"
            self.cursor.execute(
                query,
                tuple(
                    value,
                ),
            )

        self.connection.commit()

    def check_url_has_schema(self, url: str) -> bool:
        if (
            self.cursor.execute(
                f"SELECT url FROM {self.table_name} WHERE url = ?", (url,)
            ).fetchone()
            is not None
        ):
            return True
        return False

    def get_schema(self, schema_id: str) -> SchemaSearchResult:

        result = self.cursor.execute(
            f"SELECT schema_type, pickled_schema FROM {self.table_name} WHERE schema_id = ?",
            (schema_id,),
        ).fetchone()

        return SchemaSearchResult(schema_type=result[0], schema=pickle.loads(result[1]))

    def get_paths_for_url(self, url: str) -> list[PathSearchResult]:
        result: list[PathSearchResult] = list()
        for item in self.cursor.execute(
            f"SELECT schema_id, path FROM {self.table_name} WHERE url = ?", (url,)
        ).fetchall():
            result.append(PathSearchResult(id=item[0], path=item[1]))

        return result

    def close_connection(self) -> None:
        self.connection.close()
