import pathlib
import ssl
from contextlib import AbstractAsyncContextManager

import httpx


class ResourceDownloader(AbstractAsyncContextManager):
    """
    Class used for downloading content from the web
    """

    async def __aexit__(self, exc_type, exc_value, traceback, /):
        pass

    def __init__(self):
        self._ctx = ssl.create_default_context(
            cafile=pathlib.Path.home().as_posix() + r"/.mitmproxy\mitmproxy-ca-cert.pem"
        )

    async def get(self, url, use_proxy_certificate: bool = True) -> httpx.Response:
        """
        Downloads the resource associated with the url
        :param use_proxy_certificate: Use the proxy's certificate
        :param url: The location of the resource
        :return: A httpx.Response object
        """
        async with httpx.AsyncClient(
            verify=self._ctx if use_proxy_certificate else None
        ) as client:
            response = await client.get(url, follow_redirects=True)
        return response
