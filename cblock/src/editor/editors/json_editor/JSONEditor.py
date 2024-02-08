import json

from src.content_analyzer.ContentAnalyzerInterface import ContentAnalyzerInterface
from src.schemas.json_schema.JSONSchema import JSONSchema


class JSONEditor:
    content_analyzer: ContentAnalyzerInterface

    def __init__(self, content_analyzer: ContentAnalyzerInterface):
        self.content_analyzer = content_analyzer

    def edit(self, input_raw: str, schema: JSONSchema) -> dict:
        try:
            input_decoded: dict = json.loads(input_raw)

            """if schema.value_type == ValueType.DICT:
                for key, value in schema.value.items():
                    input_decoded[key] = edit_item(input_decoded[key], schema.value[key])
            elif schema.value_type == ValueType.LIST:
                for item in input_decoded:
                    item = edit_item(item, schema.value)
            elif schema.value_type == ValueType.LEAF:
                input_decoded"""

        except json.decoder.JSONDecodeError:
            pass
