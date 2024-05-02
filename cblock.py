import asyncio
import logging
import signal
import sys
import threading

from cblock_addon import CBlockAddonMain
from mitmproxy.mitmproxy import options
from mitmproxy.mitmproxy.tools import dump
from os_tools.OSManagerFactory import get_os_manager
from os_tools.OSManagerInterface import OSManagerInterface


async def create_mitm_master(host, port) -> dump.DumpMaster:
    """
    Create a mitmproxy DumpMaster, but withour starting it
    """

    opts = options.Options(listen_host=host, listen_port=port)

    master = dump.DumpMaster(
        opts,
        with_termlog=False,  # enable to see logs
        with_dumper=False,
    )

    master.addons.add(CBlockAddonMain())

    return master


async def start_master(master: dump.DumpMaster):
    """
    Start the passed master
    """
    await master.run()


class CBlock:
    def __init__(self):
        logging.getLogger(__name__)
        logging.getLogger().setLevel(logging.INFO)

    def run(self):
        host = "localhost"
        port = 8080

        # get OSManager, exit if the OS isn't supported
        try:
            self.os_manager: OSManagerInterface = get_os_manager()
        except RuntimeError as e:
            logging.error(e)
            sys.exit(0)

        self.os_manager.activate_proxy(host=host, port=port)

        # catch shutdown signals
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        self._start_async_event_loop()

        # done like this in order to have the master object that's needed to shut down later
        master = self._run_in_event_loop(create_mitm_master(host, port))

        # wait for master to be returned
        while not master.done():
            pass

        master = master.result()

        self._run_in_event_loop(start_master(master))

        print("ContentBlock has started\nPress Ctrl+C to exit")

        # remove later
        value = ""
        while value != "exit":
            value = input("Enter command (exit): ")

        master.shutdown()
        self._shutdown()

    def _shutdown(self, *_):
        print("CBlock says goodbye :)")
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