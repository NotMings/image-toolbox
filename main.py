"""图片工具箱入口：带参数时运行命令行模式，不带参数时启动图形界面。"""

import sys


def main():
    """根据是否带参数选择运行模式，返回进程退出码。"""
    if len(sys.argv) > 1:
        from app.cli import main as cli_main

        return cli_main(sys.argv[1:])

    from app.gui import run

    return run()


if __name__ == '__main__':
    sys.exit(main())
