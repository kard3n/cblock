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
            if string[pos - 1] == "\\":
                result = result[:-1] + string[pos]
            else:
                result += string[pos]
            pos += 1

    return result


def count_continuous(string: str, symbol: str, pos: int) -> int:
    result: int = 0
    while string[pos] == symbol:
        result += 1
        pos += 1

    return result


def extract_until_symbols(
    string: str, symbols: list[str], start_pos: int | None, end_pos: int | None
) -> str:
    if start_pos is None:
        start_pos = 0
    if end_pos is None:
        end_pos = len(string) - 1

    if end_pos > len(string):
        raise IndexError("End position out of range")

    result = ""
    while start_pos < end_pos and string[start_pos] not in symbols:
        result += string[start_pos]
        start_pos += 1

    if string[start_pos] not in symbols:
        raise IndexError("No end symbol in range")

    return result
