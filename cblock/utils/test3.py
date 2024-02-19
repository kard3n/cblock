from regex import regex

from src.content_analyzer.analyzers.SimpleContentAnalyzer import SimpleContentAnalyzer
from src.content_factory.ContentFactory import ContentFactory
from src.editor.editors.generic_editor.GenericEditor import GenericEditor
from src.schema.generic_schema.GenericSchemaParser import GenericSchemaParser

schema = r'pattern:"bb(?P<content>hola)bb", tags:"a", schema_id: 20'
parsed_schema = GenericSchemaParser.parse_string(schema)
input_value = "bbholabb"
print(f"Parsed schema: {parsed_schema}")
editor: GenericEditor = GenericEditor(
    content_analyzer=SimpleContentAnalyzer(), content_factory=ContentFactory()
)
editor_result = editor.extract_content(input_value=input_value, schema=parsed_schema)
print(f"Extracted content: {editor_result}")

# second
schema2 = r'''pattern:"bb(?P<content>xxholaxx)bb", tags:"e", schema_id: 20
    pattern:"xx(?P<content>hola)xx", tags:"at"'''

parsed_schema2 = GenericSchemaParser.parse_string(schema2)
input_value2 = "bbxxholaxxbb"
print(f"Parsed schema: {parsed_schema2}")
extraction_result2 = editor.extract_content(
    input_value=input_value2, schema=parsed_schema2
)
print(f"Extracted content: {extraction_result2}")
edit_result = editor.edit(input_value2, parsed_schema2)
print(f"Edited content: {edit_result}")
