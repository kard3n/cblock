import subprocess
import tomllib
import requests

from updater.common import get_newest_version_nr, version_is_higher, get_newest_version_dict


class AppUpdater:
    _newest_version_nr: str = None
    _current_version_nr: str = None
    _proxies: dict = None
    REPO_NAME: str = "kard3n/cblock"
    def __init__(self):
        pass

    def set_proxies(self, proxies: dict):
        self._proxies = proxies

    def get_newest_app_version(self) -> str:
        if self._newest_version_nr is None:
            self._newest_version_nr = get_newest_version_nr(repo_name=self.REPO_NAME, proxies=self._proxies)

        return self._newest_version_nr

    def get_current_app_version(self) -> str:
        if self._current_version_nr is None:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                self._current_version_nr = data["project"]["version"]

        return self._current_version_nr

    def new_version_available(self) -> bool:
        if self.get_current_app_version() is not None and self.get_newest_app_version() is not None and version_is_higher(self.get_newest_app_version(),self.get_current_app_version()):
            print(self._newest_version_nr)
            print(self._current_version_nr)
            return True
        return False

    def apply_update(self):
        version_dict = get_newest_version_dict(self.REPO_NAME, proxies=self._proxies)

        # Todo: fix file download
        if version_dict is None:
            print("Could not get information for the newest version.")
        else:
            file_url = None

            for asset in version_dict["assets"]:
                if asset["name"] == "cblock_setup.exe":
                    file_url = asset["browser_download_url"]
                    break

            if file_url is None:
                print("Newest version does not contain an installer, aborting update.")
            else:
                print("Downloading installer...")
                try:
                    asset_response = requests.get(file_url, timeout=12.0, proxies=self._proxies)
                except requests.exceptions.RequestException as e:
                    asset_response = None

                if asset_response is None:
                    print(
                        f"Could not download the installer file: Unknown Error"
                    )
                elif asset_response.status_code != 200:
                    print(f"Could not download the installer file{asset_response.status_code}")
                elif asset_response.status_code == 200:
                    # Save exe
                    with open("cblock_setup.exe", "wb") as file:
                        file.write(asset_response.content)

                subprocess.Popen(
                    [
                        "cblock_setup.exe",
                        "/SILENT",
                        "/CLOSEAPPLICATIONS",
                        "/RESTARTAPPLICATIONS",
                    ]
                )  # Or /VERYSILENT for no popup
