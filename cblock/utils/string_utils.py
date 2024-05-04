# returns new pos after all whitespaces and linebreaks
def jump_whitespaces_linebreaks(string: str, pos: int) -> int:
    while string[pos] in ["\n", " "]:
        pos += 1

    return pos


def count_whitespaces(string: str, pos: int) -> int:
    while string[pos] == " ":
        pos += 1

    return pos


def split_safe(string: str, symbol: str = ",") -> list[str]:
    result: list[str] = []
    temp: str = ""
    pos: int = 0
    while pos < len(string):
        if string[pos] == symbol and string[pos - 1] != "\\":
            result.append(temp.__str__().strip(" ").rstrip(" "))
            temp = ""
        else:
            if string[pos] == symbol and string[pos - 1] == "\\":
                temp = temp[:-1] + string[pos]
            else:
                temp += string[pos]
        pos += 1

    result.append(temp.__str__().strip(" ").rstrip(" "))

    return result


def extract_from_inbetween_symbol(string: str, symbol: str) -> str:
    pos: int = jump_whitespaces_linebreaks(string, 0)
    result: str = ""

    if string[pos] == symbol:
        pos += 1

    while pos < len(string):
        if string[pos] == symbol and string[pos - 1] != "\\":
            break
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
