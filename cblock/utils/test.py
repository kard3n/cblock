from src.schema.generic_schema.GenericSchemaParser import GenericSchemaParser
from src.schema.json_schema.JSONSchemaParser import JSONSchemaParser

schema: str = """{"second_name"e: {"dicty": "Big"}, "firstName"p: "John", }"""
schema_: str = (
    """{"second_name"e: {"firstName"t: "John", "life"s: "Summary of his life"}, }"""
)

schema2: str = '''{"contained_list"e: [{"picture"p(testName):"pic.jpg",}]}"'''

schema3: str = '''{"contained_dictionary"e:{"picture"p:"pic.jpg,"},}"'''
schema4: str = (
    '''{"contained_dictionary"e:{"dict2":{"firstName"t: "John"},"picture"p:"pic.jpg",}}"'''
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

print(f"Result: {JSONSchemaParser.parse_string(schema_)}\n")

print(f"Result: {JSONSchemaParser.parse_string(schema2)}\n")

print(f"Result: {JSONSchemaParser.parse_string(schema3)}\n")

print(f"Result: {JSONSchemaParser.parse_string(schema4)}")

print(f"Result: {JSONSchemaParser.parse_string(yahoo_schema)}")
