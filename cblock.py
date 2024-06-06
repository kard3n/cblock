import asyncio
import logging
import pathlib
import signal
import sys
import threading
import time

from cblock_addon import CBlockAddonMain
from configuration.Configuration import Configuration
from content_classifier.ClassifierManager import ClassifierManager
from mitmproxy.mitmproxy import options
from mitmproxy.mitmproxy.tools import dump
from os_tools.OSManagerFactory import get_os_manager
from os_tools.OSManagerInterface import OSManagerInterface


async def create_mitm_master(
    config: Configuration,
    classifier_manager: ClassifierManager,
    shutdown_event: threading.Event,
) -> dump.DumpMaster:
    """
    Create a mitmproxy DumpMaster, but without starting it
    """

    opts = options.Options(
        listen_host=config.proxy_host, listen_port=int(config.proxy_port)
    )

    master = dump.DumpMaster(
        opts,
        with_termlog=True,  # enable to see logs. Disabling it stops all logging for some reason
        with_dumper=False,
    )

    master.addons.add(CBlockAddonMain(config, classifier_manager, shutdown_event))

    return master


async def start_master(master: dump.DumpMaster):
    """
    Start the passed master
    """
    await master.run()


class CBlock:
    def __init__(self, config: Configuration):
        self.config = config

        self.classifier_manager = ClassifierManager(
            classifier_directory=pathlib.Path(__file__).parent.resolve().as_posix()
            + "/classifiers"
        )

        if not len(self.classifier_manager.classifier_info.keys()):
            print("Error: no classifiers found. Aborting.")
            sys.exit(1)

        if not config.classifier in self.classifier_manager.classifier_info.keys():
            print(
                "Error: classifier set in configuration not found. Please choose one of the following:"
            )
            for key in self.classifier_manager.classifier_info.keys():
                print(
                    f"\t{key}: {self.classifier_manager.classifier_info[key].description}"
                )

            print("Aborting...")
            sys.exit(1)

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

        # install certificate if it's the first run
        if self.config.is_first_run == "True":
            print(
                "\nIt appears ContentBlock is starting for the first time."
                + "\n\tAccept the prompt to allow the installation of the required certificates."
                + "\n\tIf you face certificate errors, try to reinstall the certificates from the settings of the GUI"
                + "\n\tWhen using Firefox, please follow the instructions here: http://mitm.it/"
                + "\n\tIn case of any other errors regarding certificates, contact the developer"
                + " or search in mitmproxy's documentation.\n"
            )
            self.os_manager.install_certificates()

            self.config.set_attribute("is_first_run", "False")

        self.shutdown_event = threading.Event()

        # catch shutdown signals
        signal.signal(signal.SIGINT, self.set_shutdown_event)
        signal.signal(signal.SIGTERM, self.set_shutdown_event)

        self._start_async_event_loop()

        # done like this in order to have the master object that's needed to shut down later
        master = self._run_in_event_loop(
            create_mitm_master(
                self.config, self.classifier_manager, self.shutdown_event
            )
        )

        # wait for master to be returned
        while not master.done():
            pass

        self.master = master.result()

        self._run_in_event_loop(start_master(self.master))

        print(
            "ContentBlock has started up successfully"
            + f"\n\tThe GUI is available at http://{self.config.application_url}/"
            + "\n\tPress Ctrl+C to exit"
        )

        # self.shutdown_event.wait() doesn't allow stopping via Ctrl+C as signals never get captured
        while not self.shutdown_event.is_set():
            time.sleep(
                0.33
            )  # This way it still catches the signals (CTRL-C) without using too much performance

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
