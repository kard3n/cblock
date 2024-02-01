from src.content_editor.editors.json_editor.ContentTag import ContentTag
from utils.json_schema_parser import JsonSchemaParser

schema: str = '''"firstName"t: "John"'''
schema2: str = '''"contained_list"r: [{"picture"p:"pic.jpg",}]"'''

schema3: str = '''"contained_dictionary"r: {"picture"p:"pic.jpg",}"'''

print(ContentTag('r').name)

print(f"Result: {JsonSchemaParser.parse_schema(schema)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema2)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema3)}\n")