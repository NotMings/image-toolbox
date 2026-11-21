# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包配置：单文件窗口程序（GUI 无控制台），命令行模式自行接上终端。
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.png'],
)
