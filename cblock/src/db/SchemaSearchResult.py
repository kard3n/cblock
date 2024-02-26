from dataclasses import dataclass


@dataclass
class SchemaSearchResult:
    schema_type: str  # type of the schema
    schema: str  # vale uf the schema, in string form
