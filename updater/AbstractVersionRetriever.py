from abc import ABC, abstractmethod


class AbstractVersionRetriever(ABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    async def get_latest_version_number(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def get_latest_installer_url(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def get_latest_tarball_url(
        self, repo_name: str, use_proxy_certificate: bool = True
    ) -> str:
        raise NotImplementedError("Not yet implemented")
