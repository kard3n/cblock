import json
import os
import shutil
import tarfile

import requests


class SchemaUpdater:
    @staticmethod
    def strip_version(version_string: str) -> str:
        version_string.lstrip("v")
        if version_string.count("-") > 0:
            version_string = version_string[0 : version_string.index("-")]

        return version_string

    @staticmethod
    def version_is_higher(version_higher: str, version_lower: str):
        """
        Returns true when version_higher > version_lower
        :param version_higher:
        :param version_lower:
        :return:
        """

        version_higher = SchemaUpdater.strip_version(version_higher).split(".")
        version_lower = SchemaUpdater.strip_version(version_lower).split(".")

        for num_high, num_low in zip(version_higher, version_lower):
            if num_high > num_low:
                return True
            elif num_high < num_low:
                return False

        return False

    @staticmethod
    async def update_schema_source(
        schema_source: str, current_version: str
    ) -> str | None:
        version_response = None
        try:
            version_response = requests.get(
                f"https://api.github.com/repos/{schema_source}/releases/latest",
                timeout=3.5,
            )
        except Exception:
            return None

        response_json = version_response.json()

        if version_response is None:
            print(
                f"Could not retrieve version information for schema {schema_source}: Other Error"
            )
        elif version_response.status_code != 200:
            print(
                f"Could not retrieve version information for schema {schema_source}: {version_response.status_code}"
            )
        elif current_version == "" or SchemaUpdater.version_is_higher(
            response_json["name"], current_version
        ):
            print(f"Downloading update for schema repository '{schema_source}'")

            directory_name: str = "schemas/" + schema_source.replace("/", "&")
            filename: str = f"{directory_name}/{schema_source.replace("/", "&")}.tar.gz"

            asset_response = None
            try:
                asset_response = requests.get(response_json["tarball_url"], timeout=6.5)
            except Exception as e:
                return None

            if asset_response is None:
                print(
                    f"Could not download update for schema repository '{schema_source}': Other Error"
                )
            elif asset_response.status_code == 200:
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
                        f"Successfully updated schema repository '{schema_source}' from '{current_version}' to {response_json["name"]}"
                    )
                    return response_json["name"]
                except tarfile.TarError:
                    print(f"Could not extract tarball: {filename}")
            else:
                print(
                    f"Could not download update for schema repository '{schema_source}: {asset_response.status_code}'"
                )

        return None

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
    async def update_schemas() -> bool:
        """

        :return: True if at least one schema has been updated, False otherwise
        """
        print("Checking for schema repo updates...")
        updated = False
        with open("schemas/schema_sources.json", "rt", encoding="utf-8") as file:
            name_to_version = json.load(file)

        for schema_source in name_to_version.keys():
            result = await SchemaUpdater.update_schema_source(
                schema_source, name_to_version[schema_source]
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
