import subprocess
import winreg

from pyuac import main_requires_admin

from os_tools.OSManagerInterface import OSManagerInterface


class WindowsOSManager(OSManagerInterface):

    def __init__(self) -> None:
        self.INTERNET_SETTINGS = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_ALL_ACCESS,
        )

    def activate_proxy(self, host: str, port: int) -> None:
        winreg.SetValueEx(
            self.INTERNET_SETTINGS,
            "ProxyServer",
            0,
            winreg.REG_SZ,
            f"{host}:{str(port)}",
        )
        winreg.SetValueEx(self.INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 1)

    def deactivate_proxy(self):
        winreg.SetValueEx(self.INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 0)
