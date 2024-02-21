from src.schema.SchemaReader import SchemaReader
import sqlite3

reader: SchemaReader = SchemaReader(
    db_name="test.db", schema_location="../src/schema_definitions/"
)

reader.run()
