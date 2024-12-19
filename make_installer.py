import os
import subprocess

import PyInstaller.__main__
from pathlib import Path


def build_installer():
    # Creates executable using pyinstaller
    PyInstaller.__main__.run(
        [
            Path(__file__).parent.absolute().__str__() + "\cblock_main.py",
            "cblock.spec",
            "--noconfirm",
        ]
    )

    # Creates installer using InnoSetup
    # subprocess.run gives "PermissionError: [WinError 5] Access is denied"
    os.system(r'"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss')


if __name__ == "__main__":
    build_installer()
