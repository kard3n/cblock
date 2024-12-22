import traceback

import requests


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

def get_newest_version_nr(repo_name: str, proxies: dict|None = None) -> str|None:
    """

    :param repo_name: Name of the repository, in {OWNER}/{REPOSITORY} format
    :param proxies:
    :return: simplified version string, for example "1.2.3"
    """

    version_dict = get_newest_version_dict(repo_name, proxies)
    return strip_version(version_dict["name"]) if version_dict else None

def get_newest_version_dict(repo_name: str, proxies: dict|None = None) -> dict | None:
    """

    :param repo_name: Name of the repository, in {OWNER}/{REPOSITORY} format
    :param proxies:
    :return: release json
    """

    print(proxies)

    try:
        version_response = requests.get(
            f"https://api.github.com/repos/{repo_name}/releases/latest",
            timeout=3.5, # Or 3.5
            proxies=proxies
        )
    except Exception:
        print(traceback.format_exc())
        return None


    if version_response is None:
        print(
            f"Could not retrieve version information for schema {repo_name}: Other Error"
        )
        return None
    elif version_response.status_code != 200:
        print(
            f"Could not retrieve version information for schema {repo_name}: {version_response.status_code}"
        )
        return None

    return version_response.json()
