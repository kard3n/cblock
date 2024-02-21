from dataclasses import dataclass, field
from enum import Enum


class ValueType(Enum):
    LIST = "list"
    DICT = "dict"
    LEAF = "leaf"


@dataclass
class JSONSchema:
    tags: list = field(default_factory=list)
    schema_id: str | None = (
        None  # if another schema should be used for this content, it is specified here
    )
    value_type: ValueType | None = None
    value: any = None  # TODO | JSONSchema gives error?
