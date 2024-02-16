from src.schemas.generic_schema.GenericSchemaParser import GenericSchemaParser
from src.schemas.json_schema.JSONSchemaParser import JsonSchemaParser

schema: str = """{"second_name"e: {"dicty": "Big"}, "firstName"p: "John", }"""
schema_: str = (
    """{"second_name"e: {"firstName"t: "John", "life"s: "Summary of his life"}, }"""
)

schema2: str = '''{"contained_list"e: [{"picture"p:"pic.jpg",}]}"'''

schema3: str = '''{"contained_dictionary"r:{"picture"p:"pic.jpg,"},}"'''
schema4: str = (
    '''{"contained_dictionary"r:{"dict2":{"firstName"t: "John"},"picture"p:"pic.jpg",}}"'''
)

yahoo_schema: str = """{
  "items":[{"data":{"partenerData":{"summary":"This is a summary"}}}]
}"""

"""d: dict = {"list_": [{"hi": "there", "Good": "Luck"}]}
print(d)
for item in d["list_"]:
    print(item)
print(d["list_"])"""


# print(ContentTag('r').name)

# print([e.value for e in ContentTag])

# print(f"Result: {JsonSchemaParser.parse_schema(schema)}\n")

print(f"Result: {JsonSchemaParser.parse_schema(schema_)}\n")

# print(f"Result: {JsonSchemaParser.parse_schema(schema2)}\n")

# print(f"Result: {JsonSchemaParser.parse_schema(schema3)}\n")

# print(f"Result: {JsonSchemaParser.parse_schema(schema4)}")

# print(f"Result: {JsonSchemaParser.parse_schema(yahoo_schema)}")

generic_schema: str = """open:"a", close:"b", schema_id: 1234"""
generic_schema2: str = """open:"a", close:"b", schema_id: 1234
    open:"c", close:"d", schema_id: 1"""

# print(GenericSchemaParser.parse_element_single(generic_schema))

print(GenericSchemaParser.parse_string(generic_schema))

print(GenericSchemaParser.parse_string(generic_schema2))
