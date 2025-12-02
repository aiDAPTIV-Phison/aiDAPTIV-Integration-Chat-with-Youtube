# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 文件用于打包 Streamlit 应用
"""

import os
from pathlib import Path

block_cipher = None

# 获取项目根目录
project_root = Path(SPECPATH)

# 收集所有需要的数据文件
datas = [
    ('utils', 'utils'),
    ('aiDAPTIV_Files', 'aiDAPTIV_Files'),
]

# 收集 Streamlit 的所有数据文件（如果已安装）
try:
    import streamlit
    streamlit_path = Path(streamlit.__file__).parent
    datas.append((str(streamlit_path / 'static'), 'streamlit/static'))
    datas.append((str(streamlit_path / 'runtime'), 'streamlit/runtime'))
except ImportError:
    # 如果 streamlit 未安装，PyInstaller 会自动收集
    pass

a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'youtube_transcript_api',
        'youtube_transcript_api._errors',
        'youtube_transcript_api._transcripts',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

