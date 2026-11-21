"""Image Toolbox 入口：不带参数启动图形界面，带参数运行命令行模式。"""

import ctypes
import os
import sys

from app.cli import main as cli_main
from app.gui import run


def _ensure_console():
    """打包成窗口程序后，命令行模式需要重新接上终端或管道的标准输出。"""
    if sys.platform != 'win32':
        return
    if sys.stdout is not None and sys.stderr is not None:
        return

    import msvcrt

    kernel32 = ctypes.windll.kernel32
    kernel32.GetStdHandle.restype = ctypes.c_void_p
    invalid_handle = ctypes.c_void_p(-1).value

    def reopen(handle, mode):
        if not handle or handle == invalid_handle:
            return None
        try:
            fd = msvcrt.open_osfhandle(handle, os.O_WRONLY if 'w' in mode else os.O_RDONLY)
            return os.fdopen(fd, mode, encoding='utf-8', errors='replace', buffering=1)
        except OSError:
            return None

    # 从终端、管道或文件重定向启动时，优先复用继承来的标准句柄
    stdout = reopen(kernel32.GetStdHandle(-11), 'w')
    stderr = reopen(kernel32.GetStdHandle(-12), 'w')
    if stdout is not None and stderr is not None:
        sys.stdout = stdout
        sys.stderr = stderr
        stdin = reopen(kernel32.GetStdHandle(-10), 'r')
        if stdin is not None:
            sys.stdin = stdin
        return

    # 没有可用标准句柄时（例如双击带参数运行），附加父控制台或新建一个
    if not kernel32.AttachConsole(-1):
        kernel32.AllocConsole()
    try:
        sys.stdout = open('CONOUT$', 'w', encoding='utf-8', errors='replace', buffering=1)
        sys.stderr = open('CONOUT$', 'w', encoding='utf-8', errors='replace', buffering=1)
        sys.stdin = open('CONIN$', 'r', encoding='utf-8', errors='replace')
    except OSError:
        pass


def main():
    """根据是否带参数选择运行模式，返回进程退出码。"""
    if len(sys.argv) > 1:
        _ensure_console()
        return cli_main(sys.argv[1:])

    return run()


if __name__ == '__main__':
    sys.exit(main())
