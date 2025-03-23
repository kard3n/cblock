def strip_version(version_string: str) -> str:
    version_string = version_string.lstrip("v")
    if version_string.count("-") > 0:
        version_string = version_string[0 : version_string.index("-")]

    return version_string


def version_is_higher(version_higher: str, version_lower: str):
    """
    Returns true when version_higher > version_lower
    :param version_higher: in "major.minor.patch" format
    :param version_lower: in "major.minor.patch" format
    :return:
    """

    if version_higher is None or version_lower is None:
        return False

    version_higher = version_higher.split(".")
    version_lower = version_lower.split(".")

    for num_high, num_low in zip(version_higher, version_lower):
        if num_high > num_low:
            return True
        elif num_high < num_low:
            return False

    return False
