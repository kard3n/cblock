import os

from regex import regex

from db.SQLiteManager import SQLiteManager
from schema.parser.GenericSchemaParser import GenericSchemaParser
from schema.parser.JSONSchemaParser import JSONSchemaParser
from schema.parser.SchemaReader import SchemaReader
from utils.string_utils import split_safe, extract_from_inbetween_symbol


# the problem is probably extract_from_inbetween_symbol
test = extract_from_inbetween_symbol(r"pattern:'\\t\\'"[8:], "'")
print(12)
print(test)
print(12)
# print(regex.compile(test))

print(os.getcwd())
schema_reader: SchemaReader = SchemaReader(
    db_manager=SQLiteManager(database_name="cb_database.db", table_name="cb_schema"),
    schema_location=os.getcwd() + "/schema_definitions",
)
schema_reader.run()

text = r"""[["wrb.fr","HOnZud","[\"ghfypsres\",[\"For you\",\"Recommended based on your interests\",[[[13,[13,\"CBMibmh0dHBzOi8vd3d3LmJsb29tYmVyZy5jb20vbmV3cy9hcnRpY2xlcy8yMDI0LTAzLTE5L3BvZGNhc3QtdGhlLWNvbnNlcXVlbmNlcy1vZi1lbG9uLW11c2stcy1kb24tbGVtb24taW1wbG9zaW9u0gEA\"],\"Podcast: The Consequences of Elon Musk’s Don Lemon Implosion\",null,[1710885832],null,\"https://www.bloomberg.com/news/articles/2024-03-19/podcast-the-consequences-of-elon-musk-s-don-lemon-implosion\",null,[[\"/attachments/CC8iK0NnNVNXako2TlZRMldVWkdOMlIyVFJERUF4aW1CU2dLTWdZdDBJWjJVQU0\",null,140,140,null,\"CC8iK0NnNVNXako2TlZRMldVWkdOMlIyVFJERUF4aW1CU2dLTWdZdDBJWjJVQU0\"]],null,[12,[12,"""
for match in regex.compile(r'\[\[13,\[13,\\".*?"\],\\"(?P<content>.*?)\E\"').finditer(
    text
):
    print(match.group("content"))
# works in pythex: \[\[13,\[13,\\".*?"\],\\"(?P<content>.*?)\"
