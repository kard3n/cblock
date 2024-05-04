import platform

from os_tools.OSManagerInterface import OSManagerInterface
from os_tools.WindowsOSManager import WindowsOSManager


def get_os_manager() -> OSManagerInterface:
    match platform.system():
        case "Windows":
            return WindowsOSManager()
        case "Darwin":
            raise NotImplementedError("MAC OS is not yet supported")
        case "Linux":
            raise NotImplementedError("Linux is not yet supported")
        case _:
            raise RuntimeError("Unsupported OS")
