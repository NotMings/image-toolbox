# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置：单文件、控制台程序，带图标、assets 和翻译文件。
# 用法：pyinstaller image-toolbox.spec


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # 资源目录和翻译文件需要一起打包，否则打包后图标/多语言会失效
    datas=[('assets', 'assets'), ('app/locales', 'app/locales')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='image-toolbox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.png'],
)
