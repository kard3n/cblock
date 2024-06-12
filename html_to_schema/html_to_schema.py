import sys
from dataclasses import dataclass
from typing import TextIO
from urllib.request import urlretrieve

import regex
from bs4 import BeautifulSoup, Tag, NavigableString, Script, Stylesheet, TemplateString

sys.path.append('../cblock')
from schema.ContentTag import ContentTag

# TODO: don't compare class, but attribute dict. Blacklist some attributes such as id

@dataclass
class TagDefinition:
    name: str
    count: int
    attr_dictionary: dict
    tag: Tag


def html_to_schema(html_in: str):
    file = open("resulting_schema.cbs", "tw")
    soup = BeautifulSoup(html_in, "lxml")

    check_tag(soup.body, file)


def check_tag(tag_in: Tag, file: TextIO) -> bool:
    """
    Constructs a list of unique child tags of the provided tag based on name and class.
    :param tag_in:
    :param file:
    :return: True if a .cbs entry has been created for this or one of this tag's children.
    """
    list_of_unique_children: list[TagDefinition] = []

    to_ret = False

    for child in tag_in.children:
        if not has_twin(
            child, list_of_unique_children
        ) and type(child) not in [Script, Stylesheet, NavigableString, TemplateString]:
            list_of_unique_children.append(
                TagDefinition(
                    name=child.name,
                    count=1,
                    attr_dictionary=child.attrs,
                    tag=child,
                )
            )

    for item in list_of_unique_children:
        if item.count > 2:
            # if the item has a count > 2, it is probably a list item

            # ensure that no entry has been generated for this item's children and that it has text
            if (not check_tag(item.tag, file) and is_sentence(item.tag.text)):
                item_to_cbs(tag_in=item.tag, file=file)
                to_ret = True
        else:
            check_tag(item.tag, file)

    return to_ret


def has_twin(tag_in: Tag, list_of_unique_children: list[TagDefinition]) -> bool:
    """
    Checks if the given tag has a twin in the list. If so, sums 1 to the twins count and returns True.
    Otherwise, returns False.
    :param tag_in:
    :param list_of_unique_children:
    :return:
    """
    for possible_twin in list_of_unique_children:
        if possible_twin.name == tag_in.name and compare_dictionaries(possible_twin.attr_dictionary, tag_in.attrs):
            possible_twin.count += 1
            return True

    return False


def item_to_cbs(tag_in: Tag, file: TextIO):
    """
    Creates a cbs schema for the given tag and saves it to the file
    :param tag_in:
    :param file:
    :return: None
    """
    children_had_content: bool = False
    result = "\n" + item_to_line(tag_in, "d")
    for child in tag_in.children:
        if is_sentence(child.text) and type(child) is not NavigableString:
            for line in tag_to_cbs(child).splitlines():
                children_had_content = True
                result += "\n    " + line

    if not children_had_content:
        result = "\n" + item_to_line(tag_in, "da")

    file.write(result)


def tag_to_cbs(tag_in: Tag) -> str | None:
    """
    Creates a cbs schema for the given tag and returns it
    :param tag_in:
    :return: None
    """

    added_children: int = 0

    if tag_has_text_child(tag_in):
        return item_to_line(tag_in, "at")
    else:
        result = item_to_line(tag_in, "")
        result += "\n#" + tag_in.text.replace("\n", "")
        for child in tag_in.children:
            if type(child) is not NavigableString:
                added_children += 1

                for line in tag_to_cbs(child).splitlines():
                    result += "\n    " + line

        if added_children > 0:
            return result
        else:
            return ""

def is_sentence(text: str) -> bool:
    """
    Returns True is the text can be considered a sentence
    Args:
        text:

    Returns:

    """
    return regex.match(r"""([A-Za-z0-9\.&'",]+\s){3,}""", text) is not None

def tag_has_text_child(tag_in: Tag) -> bool:
    """
    Returns True if the given Tag has at least one text element that has the form of a text (at least two words)
    """
    for child in tag_in.children:
        if type(child) is NavigableString and is_sentence(child.text):
            return True
    return False


def attr_in_blacklist(attr: str) -> bool:
    """
    Returns True if the attribute is blacklisted. Examples: id, name, href and data attributes
    """

    blacklist = ["id", "name", "href", "data.*"]

    for item in blacklist:
        if regex.match(item, attr) is not None:
            return True
    return False


def compare_dictionaries(dict1: dict, dict2: dict) -> bool:
    """
    Compares two dictionaries and their values
    Args:
        dict1:
        dict2:

    Returns:

    """
    if dict1.keys() != dict2.keys():
        return False

    for key in dict1.keys():
        if not attr_in_blacklist(key) and (key not in dict2.keys() or dict1[key] != dict2[key]):
            return False

    return True

def item_to_line(tag: Tag, content_tags: str) -> str:
    """
    Converts a tag to the corresponding line for in a html schema
    """
    to_ret = f"html_tag:'{tag.name}', content_tags:'{content_tags}'"
    for key in tag.attrs.keys():
        if not attr_in_blacklist(key):
            if type(tag.attrs[key]) == list:
                to_ret += f" {key}:'{' '.join(tag.attrs[key])}'"
            else:
                to_ret += f" {key}:'{tag.attrs[key]}'"
    return to_ret


if __name__ == "__main__":
    #urlretrieve(url="https://yahoo.com", filename="yahoo_test.html")
    html = open("yahoo_test.html", encoding="utf8").read()
    #html = open("test.html", encoding="utf8").read()

    html_to_schema(html)
