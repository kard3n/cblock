import json
import os
import shutil
import tarfile

from updater.AbstractVersionRetriever import AbstractVersionRetriever
from updater.GithubVersionRetriever import GithubVersionRetriever
from updater.ResourceDownloader import ResourceDownloader
from updater.utils import version_is_higher, strip_version


class SchemaUpdater:

    @staticmethod
    async def update_schema_source(
        schema_source: str, current_version: str, use_proxy_certificate: bool = True
    ) -> str | None:
        current_version_nr = strip_version(current_version)
        version_retriever: AbstractVersionRetriever = GithubVersionRetriever()

        try:
            latest_version_number = await version_retriever.get_latest_version_number(
                schema_source, use_proxy_certificate=use_proxy_certificate
            )
            latest_tarball_url = await version_retriever.get_latest_tarball_url(
                schema_source, use_proxy_certificate=use_proxy_certificate
            )
        except RuntimeError:
            print(f"Could not retrieve updates for schema {schema_source}")
        else:
            if current_version == "" or version_is_higher(
                latest_version_number, current_version_nr
            ):
                print(f"Downloading update for schema repository '{schema_source}'")

                directory_name: str = "schemas/" + schema_source.replace("/", "&")
                filename: str = (
                    f"{directory_name}/{schema_source.replace("/", "&")}.tar.gz"
                )

                try:
                    async with ResourceDownloader as downloader:
                        asset_response = await downloader.get(
                            latest_tarball_url,
                            use_proxy_certificate=use_proxy_certificate,
                        )
                except RuntimeError:
                    print(
                        f"Could not download update for schema repository '{schema_source}': Other Error"
                    )
                else:
                    # Empty the directory
                    SchemaUpdater.override_directory(directory_name=directory_name)
                    # Save tarball of new version
                    with open(filename, "wb") as file:
                        file.write(asset_response.content)

                    try:
                        members_to_extract = []
                        with tarfile.open(filename, "r:gz") as tar:
                            for member in tar.getmembers():
                                if member.name.endswith(".cbs"):
                                    member.name = member.name.split("/")[1]
                                    members_to_extract.append(member)
                            tar.extractall(
                                members=members_to_extract,
                                path=directory_name,
                                filter="tar",
                            )

                        # Remove tarball
                        os.remove(filename)

                        print(
                            f"Successfully updated schema repository '{schema_source}' from '{current_version}' to {latest_version_number}"
                        )
                        return latest_version_number
                    except tarfile.TarError:
                        print(f"Could not extract tarball: {filename}")

    @staticmethod
    def override_directory(directory_name: str):
        """
        Replaces a directory with an empty one. If it doesn't exist, creates a new one
        :param directory_name: Name of the directory
        :return:
        """

        try:
            os.mkdir(directory_name)
        except FileExistsError:
            shutil.rmtree(directory_name)
            os.mkdir(directory_name)
        except PermissionError:
            print(f"Permission denied: create directory '{directory_name}'.")

    @staticmethod
    async def update_schemas(use_proxy_certificate: bool = True) -> bool:
        """

        :return: True if at least one schema has been updated, False otherwise
        """
        print("Checking for schema repo updates...")
        updated = False
        with open("schemas/schema_sources.json", "rt", encoding="utf-8") as file:
            name_to_version = json.load(file)

        for schema_source in name_to_version.keys():
            result = await SchemaUpdater.update_schema_source(
                schema_source,
                name_to_version[schema_source],
                use_proxy_certificate=use_proxy_certificate,
            )

            if result is not None:
                name_to_version[schema_source] = result
                updated = True

            # print(response.json()["body"]) # Release notes

        with open("schemas/schema_sources.json", "wt", encoding="utf-8") as file:
            json.dump(name_to_version, file, indent=4, ensure_ascii=True)

        if not updated:
            print("All schema repos are up-to-date")

        return updated
