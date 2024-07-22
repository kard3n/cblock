from dataclasses import dataclass


@dataclass
class SchemaDefinition:
    """Used to store the values of a schema for later insertion into a database"""

    schema_id: str
    url: str
    path: str
    schema_type: str
    allowed_subdomains: list[str]
    pickled_specialized_schema: bytes
