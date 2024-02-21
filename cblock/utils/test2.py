import json

from src.content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from src.content_factory.ContentFactory import ContentFactory
from src.editor.editors.json_editor.JSONEditor import JSONEditor
from src.schema.json_schema.JSONSchemaParser import JSONSchemaParser

schema: str = (
    """{"first_item"e: {"dicty"at: "Big", "list": [{"item"as: "items value"}]}, "second_item"eap: "John", }"""
)
parsed_schema = JSONSchemaParser.parse_string(schema)
test_value: str = (
    """{"first_item": {"dicty": "Big", "list": [{"item": "items value"}, {"item": "items value"}]}, "second_item": "John"}"""
)

editor: JSONEditor = JSONEditor(
    content_analyzer=SimpleContentAnalyzer(), content_factory=ContentFactory()
)
print(f"Parsed schema: {parsed_schema}")

result: str = editor.extract_content(
    input_value=json.loads(test_value), schema=parsed_schema
)

print(f"Extraction result: {result}")

action_result = editor.apply_action(
    json.loads(test_value), schema=parsed_schema, content=ContentFactory().get_content()
)


print(f"Action result: {action_result}")

editor_result = editor.edit(input_raw=test_value, schema=parsed_schema)

print(f"Editor result: {editor_result}")
