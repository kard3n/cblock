from dataclasses import dataclass, field
from enum import Enum

from src.content_editor.editors.json_editor.ContentTag import ContentTag


class ValueType(Enum):
    LIST = 'list',
    DICT = 'dict',
    LEAF = 'leaf'


@dataclass
class ElementContainer:
    tags: list = field(default_factory=list)
    value_type: ValueType | None = None
    value: dict | str | None = None

