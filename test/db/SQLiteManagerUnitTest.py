import os
import pickle
import unittest

from db.PathSearchResult import PathSearchResult
from db.SQLiteManager import SQLiteManager
from db.SchemaDefinition import SchemaDefinition
from db.SchemaSearchResult import SchemaSearchResult
from schema.json_schema.JSONSchema import JSONSchema
from test import test_utils


class SQLiteManagerUnitTest(unittest.TestCase):
    def setUp(self):
        self.schema = JSONSchema()
        self.schema_definition: SchemaDefinition = SchemaDefinition(
            schema_id=test_utils.random_string(10),
            allowed_subdomains=[test_utils.random_string(10), ""],
            path=test_utils.random_string(10),
            pickled_specialized_schema=pickle.dumps(self.schema),
            schema_type=test_utils.random_string(10),
            url=test_utils.random_string(10),
        )
        self.db_manager = SQLiteManager(database_name="test.db")

    def tearDown(self):
        self.db_manager.close_connection()
        # delete db
        os.remove("test.db")

    def test_initialize_database(self):
        self.assertEqual(
            [],
            [
                name
                for name in self.db_manager.cursor.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ],
        )

        self.db_manager.initialize_database()

        self.assertEqual(
            [("schemas",), ("subdomains",)],
            [
                name
                for name in self.db_manager.cursor.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ],
        )

    def test_has_database(self):
        self.assertFalse(self.db_manager.has_database())

        self.db_manager.initialize_database()

        self.assertTrue(self.db_manager.has_database())

    def test_insert(self):
        self.db_manager.initialize_database()

        self.db_manager.insert(values=[self.schema_definition])

        self.assertEqual(
            [
                (
                    self.schema_definition.schema_id,
                    self.schema_definition.url,
                    self.schema_definition.path,
                    self.schema_definition.schema_type,
                    self.schema_definition.pickled_specialized_schema,
                )
            ],
            [
                schema
                for schema in self.db_manager.cursor.execute(
                    f"SELECT schema_id, url, path, schema_type, pickled_schema FROM schemas"
                ).fetchall()
            ],
        )

        self.assertEqual(
            [
                (
                    self.schema_definition.schema_id,
                    self.schema_definition.allowed_subdomains[0],
                ),
                (
                    self.schema_definition.schema_id,
                    self.schema_definition.allowed_subdomains[1],
                ),
            ],
            [
                schema
                for schema in self.db_manager.cursor.execute(
                    f"SELECT schema_id, subdomain FROM subdomains"
                ).fetchall()
            ],
        )

    def test_get_schema(self):
        self.db_manager.initialize_database()
        self.db_manager.insert(values=[self.schema_definition])

        self.assertEqual(
            SchemaSearchResult(
                schema_type=self.schema_definition.schema_type,
                schema=self.schema,
            ),
            self.db_manager.get_schema(self.schema_definition.schema_id),
        )

    def test_get_paths_for_url(self):
        self.db_manager.initialize_database()
        self.db_manager.insert(values=[self.schema_definition])

        self.assertEqual(
            [
                PathSearchResult(
                    id=self.schema_definition.schema_id,
                    path=self.schema_definition.path,
                    allowed_subdomains=self.schema_definition.allowed_subdomains,
                )
            ],
            self.db_manager.get_paths_for_url(self.schema_definition.url),
        )
