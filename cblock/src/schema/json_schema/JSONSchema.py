from dataclasses import dataclass, field
from enum import Enum


class ValueType(Enum):
    LIST = "list"
    DICT = "dict"
    LEAF = "leaf"


@dataclass
class JSONSchema:
    tags: list = field(default_factory=list)
    editor_id: int | None = (
        None  # if another editor should be used for this content, it is specified here
    )
    value_type: ValueType | None = None
    value: any = None  # TODO | JSONSchema gives error?
