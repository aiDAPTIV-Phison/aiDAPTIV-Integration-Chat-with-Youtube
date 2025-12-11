# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 文件用于打包 Streamlit 应用
"""

import os
import site
from pathlib import Path

block_cipher = None

# 获取项目根目录
project_root = Path(SPECPATH)

# 收集所有需要的数据文件
datas = [
    ('utils', 'utils'),
    ('aiDAPTIV_Files', 'aiDAPTIV_Files'),
    ('main.py', '.'),  # 将 api.py 打包到根目录
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

# 收集包元数据文件（.dist-info 目录）
# 这对于 importlib.metadata 正常工作至关重要
def collect_metadata_dirs():
    """收集所有已安装包的元数据目录"""
    metadata_dirs = []
    # 关键包名列表（支持多种命名格式）
    key_packages = ['streamlit', 'youtube_transcript_api', 'youtube-transcript-api', 
                    'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna']
    # 获取所有 site-packages 目录
    for site_packages in site.getsitepackages():
        site_path = Path(site_packages)
        if site_path.exists():
            # 查找所有 .dist-info 目录
            for dist_info in site_path.glob('*.dist-info'):
                # 提取包名（.dist-info 前的部分，去掉版本号）
                pkg_name = dist_info.stem.split('-')[0].lower().replace('_', '-')
                # 检查是否是关键包（支持带下划线和连字符的变体）
                if (pkg_name in key_packages or 
                    pkg_name.replace('-', '_') in key_packages or
                    pkg_name.replace('_', '-') in key_packages):
                    metadata_dirs.append((str(dist_info), dist_info.name))
    return metadata_dirs

# 添加元数据目录
datas.extend(collect_metadata_dirs())

a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.version',
        'youtube_transcript_api',
        'youtube_transcript_api._errors',
        'youtube_transcript_api._transcripts',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'importlib.metadata',
        'importlib.metadata._adapters',
        'importlib.metadata._collections',
        'importlib.metadata._functools',
        'importlib.metadata._itertools',
        'importlib.metadata._meta',
        'importlib.metadata._text',
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
    console=True,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

