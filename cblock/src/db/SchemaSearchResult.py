from dataclasses import dataclass


@dataclass
class SchemaSearchResult:
    schema_type: str
    schema: str
