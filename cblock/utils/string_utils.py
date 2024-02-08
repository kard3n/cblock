# returns new pos after all whitespaces and linebreaks
def jump_whitespaces_linebreaks(string: str, pos: int) -> int:
    while string[pos] in ["\n", " "]:
        pos += 1

    return pos


def jump_whitespaces(string: str, pos: int) -> int:
    while string[pos] == " ":
        pos += 1

    return pos


def extract_from_inbetween_symbol(string: str, symbol: str) -> str:
    pos: int = jump_whitespaces_linebreaks(string, 0)
    result: str = ""
    if string[pos] == symbol:
        pos += 1
        while not (string[pos] == symbol and string[pos - 1] != "\\"):
            result += string[pos]
            pos += 1

    return result


def count_continuous(string: str, symbol: str, pos: int) -> int:
    result: int = 0
    while string[pos] == symbol:
        result += 1
        pos += 1

    return result
