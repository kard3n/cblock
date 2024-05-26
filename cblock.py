import asyncio
import logging
import signal
import sys
import threading

from cblock_addon import CBlockAddonMain
from configuration.Configuration import Configuration
from mitmproxy.mitmproxy import options
from mitmproxy.mitmproxy.tools import dump
from os_tools.OSManagerFactory import get_os_manager
from os_tools.OSManagerInterface import OSManagerInterface


async def create_mitm_master(config, shutdown_event) -> dump.DumpMaster:
    """
    Create a mitmproxy DumpMaster, but withour starting it
    """

    opts = options.Options(
        listen_host=config.proxy_host, listen_port=int(config.proxy_port)
    )

    master = dump.DumpMaster(
        opts,
        with_termlog=False,  # enable to see logs. Disabling it stops all logging for some reason
        with_dumper=False,
    )

    master.addons.add(CBlockAddonMain(config, shutdown_event))

    return master


async def start_master(master: dump.DumpMaster):
    """
    Start the passed master
    """
    await master.run()


class CBlock:
    def __init__(self, config: Configuration):
        self.config = config

    def run(self):

        # get OSManager, exit if the OS isn't supported
        try:
            self.os_manager: OSManagerInterface = get_os_manager()
        except RuntimeError as e:
            logging.error(e)
            sys.exit(0)

        self.os_manager.activate_proxy(
            host=self.config.proxy_host,
            port=self.config.proxy_port,
        )

        self.shutdown_event = threading.Event()

        # catch shutdown signals
        signal.signal(signal.SIGINT, self.set_shutdown_event)
        signal.signal(signal.SIGTERM, self.set_shutdown_event)

        self._start_async_event_loop()

        # done like this in order to have the master object that's needed to shut down later
        master = self._run_in_event_loop(
            create_mitm_master(self.config, self.shutdown_event)
        )

        # wait for master to be returned
        while not master.done():
            pass

        self.master = master.result()

        self._run_in_event_loop(start_master(self.master))

        print("ContentBlock has started\nPress Ctrl+C to exit")

        # self.shutdown_event.wait() doesn't allow stopping via Ctrl+C as signals never get captured
        while not self.shutdown_event.is_set():
            pass

        self._shutdown()

    def _shutdown(self, *_):
        print("CBlock says goodbye :)")
        self.master.shutdown()
        self.os_manager.deactivate_proxy()
        self._stop_async_event_loop()
        sys.exit(0)

    def set_shutdown_event(self, *_):
        self.shutdown_event.set()

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


if __name__ == "__main__":
    config = Configuration()
    cblock = CBlock(config)
    cblock.run()
