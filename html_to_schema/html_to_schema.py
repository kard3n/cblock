import sys
from dataclasses import dataclass
from typing import TextIO
from urllib.request import urlretrieve

import regex
from bs4 import (
    BeautifulSoup,
    Tag,
    NavigableString,
    Script,
    Stylesheet,
    TemplateString,
    element,
)

sys.path.append("../cblock")


@dataclass
class TagDefinition:
    name: str
    count: int
    attr_dictionary: dict
    tag: Tag


def html_to_schema(html_in: str):
    file = open("resulting_schema.cbs", "wt")
    file.write("")
    file = open("resulting_schema.cbs", "at")
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
        print(type(child))
        if not tag_type_in_blacklist(child) and "class" in child.attrs:
            print("Name: " + child.name + " Class:" + child.attrs["class"].__str__())

        if not has_twin(child, list_of_unique_children) and not tag_type_in_blacklist(
            child
        ):
            list_of_unique_children.append(
                TagDefinition(
                    name=child.name,
                    count=1,
                    attr_dictionary=clean_attribute_dict(child.attrs),
                    tag=child,
                )
            )
    print(
        "    ".join(
            [
                item.name + ", " + item.attr_dictionary.__str__()
                for item in list_of_unique_children
            ]
        )
    )

    result: str = ""
    for item in list_of_unique_children:
        if item.count > 2:
            # if the item has a count > 2, it is probably a list item
            """print(item.name, item.attr_dictionary)
            print(is_sentence(f"{item.tag.text}".replace("\n", " ")))
            print(f"{item.tag.text}".replace("\n", " "))"""

            # ensure that no entry has been generated for this item's children and that it has text
            if not check_tag(item.tag, file) and is_sentence(item.tag.text):
                result += "\n" + item_to_cbs(tag_in=item.tag)
                to_ret = True
        else:
            check_tag(item.tag, file)

    if result != "":
        to_file = "\n" + item_to_line(tag=tag_in, content_tags="")
        for line in result.splitlines():
            # in case empty lines were added
            if line.strip() != "":
                to_file += "\n    " + line
        file.write(to_file)

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
        if possible_twin.name == tag_in.name and compare_dictionaries(
            possible_twin.attr_dictionary, clean_attribute_dict(tag_in.attrs)
        ):
            possible_twin.count += 1
            return True

    return False


def item_to_cbs(tag_in: Tag) -> str:
    """
    Creates a cbs schema for the given tag and saves it to the file
    :param tag_in:
    :return: None
    """
    # print(tag_in.name, tag_in.attrs)
    children_had_content: bool = False
    result = "\n" + item_to_line(tag_in, "d")
    for child in tag_in.children:
        if is_sentence(child.text) and type(child) is not NavigableString:
            for line in tag_to_cbs(child).splitlines():
                children_had_content = True
                result += "\n    " + line

    if not children_had_content:
        result = "\n" + item_to_line(tag_in, "da")

    return result


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
        # result += "\n#" + tag_in.text.replace("\n", "")
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
    return len(regex.findall(pattern=r"""([\w\.&'",_]+\s+){3,}""", string=text)) > 0


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

    blacklist = ["name", "href", "data.*", "src", "alt", "nonce"]

    for item in blacklist:
        if regex.match(item, attr) is not None:
            return True
    return False


def tag_type_in_blacklist(tag) -> bool:
    """
    Returns true if the given Tag is of a type that should not be processes
    :param tag:
    :return:
    """
    if type(tag) in [
        Script,
        Stylesheet,
        NavigableString,
        TemplateString,
    ]:
        return True

    # in case something isn't interpreted correctly
    if tag.name in ["script", "stylesheet"]:
        return True

    return False


def clean_attribute_dict(attr_dict: dict) -> dict:
    result = {}
    for key in attr_dict.keys():
        if not attr_in_blacklist(key):
            if type(attr_dict[key]) is list:
                result[key] = clean_multival_attr_value(attr_dict[key])
            else:
                result[key] = attr_dict[key]
    return result


def clean_multival_attr_value(attrs: [str]) -> list:
    """
    Removes unnecessary values from multivalued attributes
    :param attrs:
    :return:
    """
    result = []
    for item in attrs:
        if regex.match(r"_.*", item) is None:
            result.append(item)

    return result


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
        if not attr_in_blacklist(key) and (
            key not in dict2.keys() or dict1[key] != dict2[key]
        ):
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
                to_ret += f", {key}:'{' '.join(tag.attrs[key]).replace(",", r"\,")}'"
            else:
                to_ret += f", {key}:'{tag.attrs[key].replace(",", r"\,")}'"
    return to_ret


if __name__ == "__main__":
    # urlretrieve(url="https://yahoo.com", filename="yahoo_test.html")
    html = open("yahoo_test.html", encoding="utf8").read()
    # html = open("test.html").read()

    html_to_schema(html)
