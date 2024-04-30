import winreg

from mitmproxy.mitmproxy.tools.main import mitmdump


def activate_proxy_windows():
    INTERNET_SETTINGS = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        0,
        winreg.KEY_ALL_ACCESS,
    )
    winreg.SetValueEx(
        INTERNET_SETTINGS, "ProxyServer", 0, winreg.REG_SZ, "localhost:8080"
    )
    winreg.SetValueEx(INTERNET_SETTINGS, "ProxyEnable", 0, winreg.REG_DWORD, 1)


if __name__ == "__main__":
    mitmdump(args=["-s", "cblock/cblock_addon.py"])
