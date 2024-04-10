from dataclasses import dataclass, field
from typing import Dict

from regex import Pattern

from schema.ContentTag import ContentTag


@dataclass
class HTMLSchema:
    """This class represents an HTTP schema.

    Attributes:
        html_tag (Pattern): The html tag that should be matched by this schema element, if none everything is matched (including strings). Can be a regex.
        attributes (Dict[str, Pattern]): The attributes that the element must have to be matched. The value is a regex pattern that must match against the attributes value
        edit_attributes Dict[str, list[ContentTag]]: A list of the attributes of the matched element that should be edited or their content analyzed according to the related ContentTags
        search_recursive: (bool): If set to True, a recursive search of the children of the element is performed. Otherwise only its direct children will be taken into account
        content_tags (List[ContentTag]): The content tags that apply to the matched content's value
        embedded_schema (str|None): Embedded schema to be used for the content
        children (list|None): List of child HTTP schemas
    """

    html_tag: Pattern | None = None
    attributes: Dict[str, Pattern] = field(default_factory=dict)
    attributes_to_edit: Dict[str, list[ContentTag]] = field(default_factory=dict)
    search_recursive: bool = True
    content_tags: list[ContentTag] = field(default_factory=list[ContentTag])
    embedded_schema: str | None = (
        None  # Can be specified, if a different schema (and therefore editor) should be used for the matched content
    )
    children: None | list = (
        None  # should be set to a value other than None if the schema element has children
    )
