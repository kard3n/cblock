from src.content_editor.editors.json_editor.ContentTag import ContentTag
from utils.json_schema_parser import JsonSchemaParser

schema: str = '''{"second_name"t: {"dicty": "Big"}, "firstName"t: "John", }'''
schema_: str = '''{"second_name"t: {"firstName"t: "John", "dicty": "Big"}, }'''

schema2: str = '''{"contained_list"r: [{"picture"p:"pic.jpg",}]}"'''

schema3: str = '''{"contained_dictionary"r:{"picture"p:"pic.jpg,"},}"'''
schema4: str = '''{"contained_dictionary"r:{"dict2":{"firstName"t: "John"},"picture"p:"pic.jpg",}}"'''

#print(ContentTag('r').name)

print([e.value for e in ContentTag])

print(f"Result: {JsonSchemaParser.parse_schema(schema)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema_)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema2)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema3)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema4)}")