from mitmproxy.mitmproxy.tools.main import mitmdump

if __name__ == "__main__":
    mitmdump(args=["-s", "cblock/cblock_addon.py"])
