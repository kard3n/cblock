from datetime import datetime, timedelta

import httpx

from updater.AbstractVersionRetriever import AbstractVersionRetriever
from updater.ResourceDownloader import ResourceDownloader
from updater.utils import strip_version


class GithubVersionRetriever(AbstractVersionRetriever):
    def __init__(self):
        super().__init__()

        self._release_info = {}
        # For each repo name, contains the following:
        #   latest_installer_url: str
        #   latest_version_nr: str
        #   latest_tarball_url: str
        #   information_retrieval_time: datetime

    async def __get_latest_release_info(
        self, repo_name, use_proxy_certificate: bool = True
    ):
        """
        Gets the latest release info from the given repository name.
        :param repo_name:
        :return:
        """
        async with ResourceDownloader() as downloader:
            response = await downloader.get(
                f"https://api.github.com/repos/{repo_name}/releases/latest",
                use_proxy_certificate=use_proxy_certificate,
            )

            if response.status_code == httpx.codes.OK:
                response_json = response.json()

                installer_url = None
                for asset in response_json["assets"]:
                    if asset["name"] == "cblock_setup.exe":
                        installer_url = asset["browser_download_url"]
                        break
                self._release_info[repo_name] = {
                    "latest_installer_url": installer_url,
                    "latest_tarball_url": response_json["tarball_url"],
                    "latest_version_nr": strip_version(response_json["name"]),
                    "information_retrieval_time": datetime.now(),
                }
            else:
                raise IOError(f"Failed to get latest release info for {repo_name}")

    async def __update_information(self, repo_name, use_proxy_certificate: bool = True):
        """
        Fetches information from the given repository name if it hasn't been retrieved before or is outdated
        :param repo_name:
        :return:
        """
        if not repo_name in self._release_info.keys() or self._release_info[repo_name][
            "information_retrieval_time"
        ] < datetime.now() - timedelta(minutes=3):
            try:
                await self.__get_latest_release_info(
                    repo_name, use_proxy_certificate=use_proxy_certificate
                )
            except Exception as e:
                raise RuntimeError(
                    f'Could not get information for "{repo_name}"'
                ) from e

    async def get_latest_installer_url(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        try:
            await self.__update_information(
                repo_name, use_proxy_certificate=use_proxy_certificate
            )
        except IOError as e:
            raise RuntimeError(f'Could not get information for "{repo_name}"') from e
        else:
            return self._release_info[repo_name]["latest_installer_url"]

    async def get_latest_version_number(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        try:
            await self.__update_information(
                repo_name, use_proxy_certificate=use_proxy_certificate
            )
        except IOError as e:
            raise RuntimeError(f'Could not get information for "{repo_name}"') from e
        else:
            return self._release_info[repo_name]["latest_version_nr"]

    async def get_latest_tarball_url(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        try:
            await self.__update_information(
                repo_name, use_proxy_certificate=use_proxy_certificate
            )
        except IOError as e:
            raise RuntimeError(f'Could not get information for "{repo_name}"') from e
        else:
            return self._release_info[repo_name]["latest_tarball_url"]
