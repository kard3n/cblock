# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
# nltk, sklearn.pipeline, sklearn.feature_selection and cloudpickle are needed fo the NB classifiers. Remove if they are not needed
# TODO: find a way to remove sklearn.pipeline, as it consumes a lot of disk space
hiddenimports = ['uuid', 'mitmproxy_rs', 'brotli', 'zstandard', 'wsproto', 'ruamel.yaml', 'pyparsing', 'aioquic', 'aioquic.buffer', 'aioquic.quic', 'aioquic.quic.configuration',
'aioquic.quic.connection', 'kaitaistruct', 'aioquic.h3.connection', 'h2.config', 'h2.connection', 'pyperclip', 'werkzeug', 'asgiref.compatibility', 'asgiref.wsgi', 'flask', 'ldap3',
'passlib.apache', 'pydivert', 'msgpack', 'xml.dom', 'nltk', 'sklearn.pipeline', 'cloudpickle', 'sklearn.feature_selection']
tmp_ret = collect_all('mitmproxy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('classifiers')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['cblock.py'],
    pathex=['cblock'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cblock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cblock',
)
