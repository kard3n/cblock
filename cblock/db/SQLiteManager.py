import pickle
import sqlite3

from db.DBManagerInterface import DBManagerInterface
from db.SchemaDefinition import SchemaDefinition
from db.SchemaSearchResult import SchemaSearchResult

from db.PathSearchResult import PathSearchResult


class SQLiteManager(DBManagerInterface):
    connection: sqlite3.Connection
    database_name: str
    cursor: sqlite3.Cursor
    schema_table_name: str

    def __init__(self, database_name: str) -> None:
        self.database_name = database_name
        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()
        self.schema_table_name = "schemas"
        self.subdomain_table_name = "subdomains"

    # return True if a database already exists, if not returns False
    def has_database(self) -> bool:
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.schema_table_name}'"
            ).fetchone()
            is None
            or self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.subdomain_table_name}'"
            ).fetchone()
        ):
            return False
        return True

    def initialize_database(self):
        self.create_schema_table()
        self.create_subdomain_table()

        # Commit transaction
        self.connection.commit()

    def create_schema_table(self) -> None:
        """
        Creates the schema table, and resets it if it already exists
        :return:
        """
        columns_to_index = ["url"]

        create_sentence: str = (
            f"CREATE TABLE {self.schema_table_name}(schema_id NOT NULL PRIMARY KEY, url TEXT NOT NULL, path TEXT NOT NULL, schema_type TEXT NOT NULL, pickled_schema BLOB NOT NULL) WITHOUT ROWID"
        )

        # Check if the  table exists, if so drops it
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.schema_table_name}'"
            ).fetchone()
            is not None
        ):
            self.cursor.execute(f"DROP TABLE {self.schema_table_name}")

        # Create fresh table
        self.cursor.execute(create_sentence)

        # Add indexes
        for index in columns_to_index:
            self.cursor.execute(
                f"CREATE INDEX {index}_index ON {self.schema_table_name}({index})"
            )

    def create_subdomain_table(self) -> None:
        """
        Creates the subdomain table, and resets it if it already exists
        :return:
        """

        create_sentence: str = (
            f"CREATE TABLE {self.subdomain_table_name}(schema_id NOT NULL PRIMARY KEY, subdomain TEXT NOT NULL) WITHOUT ROWID"
        )

        # Check if the table exists, if so drops it
        if (
            self.cursor.execute(
                f"SELECT name FROM sqlite_schema WHERE name='{self.subdomain_table_name}'"
            ).fetchone()
            is not None
        ):
            self.cursor.execute(f"DROP TABLE {self.subdomain_table_name}")

        # Create fresh table
        self.cursor.execute(create_sentence)

        # Add index
        self.cursor.execute(
            f"CREATE INDEX {"schema_id"}_index ON {self.subdomain_table_name}({"schema_id"})"
        )

    def make_query_parameter_question_marks(self, num_params: int) -> str:
        question_marks = "?"
        for i in range(num_params - 1):
            question_marks += ",?"
        return question_marks

    def insert(self, values: list[SchemaDefinition]) -> None:
        "[filename[:-4], url, path, schema_type, pickled_object]"
        for schema in values:
            # Insert schema
            schema_query = f"INSERT INTO {self.schema_table_name} VALUES ({self.make_query_parameter_question_marks(num_params=5)})"
            self.cursor.execute(
                schema_query,
                (
                    schema.schema_id,
                    schema.url,
                    schema.path,
                    schema.schema_type,
                    schema.pickled_specialized_schema,
                ),
            )

            # Insert allowed subdomains for schema
            subdomain_query = f"INSERT INTO {self.subdomain_table_name} VALUES ({self.make_query_parameter_question_marks(num_params=2)})"
            for allowed_subdomain in schema.allowed_subdomains:
                self.cursor.execute(
                    subdomain_query,
                    (schema.schema_id, allowed_subdomain),
                )

        self.connection.commit()

    def check_url_has_schema(self, url: str) -> bool:
        if (
            self.cursor.execute(
                f"SELECT url FROM {self.schema_table_name} WHERE url = ?", (url,)
            ).fetchone()
            is not None
        ):
            return True
        return False

    def get_schema(self, schema_id: str) -> SchemaSearchResult:

        result = self.cursor.execute(
            f"SELECT schema_type, pickled_schema FROM {self.schema_table_name} WHERE schema_id = ?",
            (schema_id,),
        ).fetchone()

        return SchemaSearchResult(schema_type=result[0], schema=pickle.loads(result[1]))

    def get_paths_for_url(self, url: str) -> list[PathSearchResult]:
        result: list[PathSearchResult] = list()
        for schema in self.cursor.execute(
            f"SELECT schema_id, path FROM {self.schema_table_name} WHERE url = ?",
            (url,),
        ).fetchall():
            allowed_subdomains = []

            # Fetch all allowed subdomains for this schema
            for subdomain in self.cursor.execute(
                f"SELECT subdomain FROM {self.subdomain_table_name} WHERE schema_id= ?",
                (schema[0],),
            ).fetchall():
                allowed_subdomains.append(subdomain[0])

            result.append(
                PathSearchResult(id=schema[0], path=schema[1], allowed_subdomains=[])
            )

        return result

    def close_connection(self) -> None:
        self.connection.close()
