import random, string

from content_factory.Content import Content


def random_string(
    length: int, include_digits: bool = False, include_special: bool = False
) -> str:
    symbols = string.ascii_letters
    if include_digits:
        symbols += string.digits
    if include_special:
        symbols += string.punctuation

    i: int = 0
    result = ""
    while i < length:
        result += random.choice(symbols)
        i += 1

    return result


def generate_content() -> Content:
    return Content(
        title=random_string(10),
        subtitle=random_string(10),
        summary=random_string(10),
        full=random_string(10),
        picture=random_string(10),
        video=random_string(10),
        audio=random_string(10),
        tags=[random_string(10)],
        link=random_string(10),
    )
