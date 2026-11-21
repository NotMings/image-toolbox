# Image Toolbox

[English](README.md) | [简体中文](README.zh_CN.md) | [繁體中文](README.zh_TW.md)

Batch image processing tool built with Python + PySide6, with both a graphical interface and a command-line mode.

## Run

Run the packaged program `dist/image-toolbox.exe`:

```powershell
.\dist\image-toolbox.exe
```

Double-click to start the graphical interface; pass arguments to use the command-line mode (English only, also works on headless systems):

```powershell
.\dist\image-toolbox.exe --help
.\dist\image-toolbox.exe -i .\photos -o .\out --format jpeg --recursive --threads 8
.\dist\image-toolbox.exe -i .\photos -o .\out --compress 100
```

View all options (English): `--help` (or `-h`); `--version` for the version.

The GUI is a windowed program and does not open a console. In command-line mode the executable attaches to the current terminal or pipe for its output.

CLI exit codes: `0` success, `1` argument/runtime error, `2` some images failed or were skipped, `3` cancelled.

## Features

- Convert: JPEG / PNG / WebP
- Compress: to a target KB, cropping when necessary
- Rename: UUID / MD5 / auto-increment number
- Multithreading: 1-128 threads
- Pause / cancel (in-flight images finish first)
- Prompts for transparent images to JPEG and duplicate output names
- The GUI detects the system language at startup (Simplified Chinese / Traditional Chinese; other languages fall back to English) and can be switched in the Language menu; the CLI is English-only

## Build

```powershell
pip install pillow pyside6 pyinstaller
pyinstaller image-toolbox.spec
```

The executable is `dist/image-toolbox.exe`. `image-toolbox.spec` configures one-file windowed mode (no console for the GUI), the icon, `assets`, and the translation files.

Translation files use English msgids and live in `app/locales/zh_CN` and `app/locales/zh_TW`. After editing them, run `python tools/build_catalogs.py` to regenerate the `.mo` files before packaging.

## Notes

- When an output file already exists, the app asks how to handle it; using an empty output folder is recommended.
- Compression has limits; a very small target may crop the image.
- Make sure you have permission to modify the original files and respect copyright.
