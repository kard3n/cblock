from abc import ABC, abstractmethod


class OSManagerInterface(ABC):

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def activate_proxy(self, host: str, port: int) -> None:
        """
        Tells the OS to use "host:port" as a proxy server.
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def deactivate_proxy(self) -> None:
        """
        Stops the OS from sending traffic through the proxy
        """
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def install_certificates(self):
        """
        Installs the required certificates for mitmproxy to work
        :return:
        """
        raise NotImplementedError("Not implemented")
