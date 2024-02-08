from dataclasses import dataclass
from re import Pattern


@dataclass
class GenericSchema:  # container for GenericSchemaElements.
    children: (  # should be specified if the schema has children that should be specified
        list
    ) = list


@dataclass
class GenericSchemaElement:
    open: Pattern = None
    close: Pattern = None
    schema_id: int | None = (
        None  # Can be specified, if a different schema (and therefore editor) should be used for the matched content
    )
    children: None | list = (
        None  # should be set to a value other than None if the schema element has children
    )
