import asyncio
import logging
import signal
import sys
import threading
from asyncio import AbstractEventLoop

from mitmproxy.mitmproxy import options
from mitmproxy.mitmproxy.tools import dump
from mitmproxy.mitmproxy.tools.main import mitmdump
from os_tools.OSManagerFactory import get_os_manager
from os_tools.OSManagerInterface import OSManagerInterface


class CBlock:
    def __init__(self):
        logging.getLogger(__name__)
        logging.getLogger().setLevel(logging.INFO)

    def run(self):

        # get OSManager, exit if the OS isn't supported
        try:
            self.os_manager: OSManagerInterface = get_os_manager()
        except RuntimeError as e:
            logging.error(e)
            sys.exit(0)

        self.os_manager.activate_proxy(host="localhost", port=8080)

        mitm_thread = threading.Thread(
            target=mitmdump, args=[["-s", "cblock/cblock_addon.py"]], daemon=True
        )
        mitm_thread.start()
        loop: AbstractEventLoop = asyncio.new_event_loop()

        # catch shutdown signals
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        logging.info(" ContentBlock has started\nPress Ctrl+C to exit")

        # remove later
        while True:
            pass

    def _shutdown(self, signum, frame):
        logging.info(" CBlock says goodbye :)")
        self.os_manager.deactivate_proxy()
        self._stop_async_event_loop()
        sys.exit(0)

    # functions for creating the async loop
    def _start_async_event_loop(
        self,
    ):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever).start()

    def _run_in_event_loop(self, awaitable):
        return asyncio.run_coroutine_threadsafe(awaitable, self.loop)

    def _stop_async_event_loop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


# entrypoint of the application
if __name__ == "__main__":
    # cblock = CBlock()
    # cblock.run()
    pass


class RequestLogger:
    def request(self, flow):
        print(flow.request)


async def start_mitm(host, port) -> dump.DumpMaster:

    opts = options.Options(listen_host=host, listen_port=port)

    master = dump.DumpMaster(
        opts,
        with_termlog=True,
        with_dumper=False,
    )

    master.addons.add(RequestLogger())

    # await master.run() # should be done like this, but master needs to be returned
    master.run()
    return master


if __name__ == "__main__":
    host = "localhost"
    port = 8080

    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever).start()
    master = asyncio.run_coroutine_threadsafe(start_mitm(host, port), loop)
    print("Hello")
    value = input("Enter command: ")
    while value != "exit":
        if value == "s":
            print("Testing shutdown")
            master.result().shutdown()
        value = input("Enter command: ")
    loop.call_soon_threadsafe(loop.stop)
