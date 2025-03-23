import subprocess
import tomllib
import traceback

from updater.AbstractVersionRetriever import AbstractVersionRetriever
from updater.ResourceDownloader import ResourceDownloader
from updater.GithubVersionRetriever import GithubVersionRetriever
from updater.utils import version_is_higher


class ApplicationUpdater:
    REPO_NAME: str = "kard3n/cblock"

    def __init__(self):
        self._version_retriever: AbstractVersionRetriever = GithubVersionRetriever()
        self._current_version_nr: str | None = None

    def get_current_application_version(self) -> str:
        if self._current_version_nr is None:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                self._current_version_nr = data["project"]["version"]

        return self._current_version_nr

    async def get_latest_application_version(
        self, use_proxy_certificate: bool = True
    ) -> str:
        try:
            return await self._version_retriever.get_latest_version_number(
                ApplicationUpdater.REPO_NAME,
                use_proxy_certificate=use_proxy_certificate,
            )
        except Exception:
            return "0.0.0"

    async def new_version_available(self, use_proxy_certificate: bool = True) -> bool:
        newest_app_version = await self._version_retriever.get_latest_version_number(
            repo_name=ApplicationUpdater.REPO_NAME,
            use_proxy_certificate=use_proxy_certificate,
        )
        if newest_app_version is not None and version_is_higher(
            newest_app_version, self.get_current_application_version()
        ):
            return True
        return False

    async def apply_update(self):
        try:
            release_file_url = await self._version_retriever.get_latest_installer_url(
                ApplicationUpdater.REPO_NAME
            )
        except Exception:
            print(traceback.print_exc())
            print("Could not get information for the newest version, aborting update.")
        else:
            if release_file_url is None:
                print("Newest version does not contain an installer, aborting update.")
            else:
                print("Downloading installer...")
                async with ResourceDownloader() as downloader:
                    asset_response = await downloader.get(release_file_url)

                if asset_response is None:
                    print(f"Could not download the installer file: Unknown Error")
                elif asset_response.status_code != 200:
                    print(
                        f"Could not download the installer file. Error code: {asset_response.status_code}"
                    )
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
