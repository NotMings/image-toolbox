#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""图片工具箱命令行模式：在没有图形界面的环境中批量处理图片。

和图形界面共用同一个程序：不带参数启动时打开图形界面，带参数时进入命令行模式。

用法示例：
    python main.py -i ./photos -o ./out --format jpeg --recursive --threads 8
    python main.py -i ./photos -o ./out --compress 100
    python main.py -i ./photos -o ./out --rename number

命令行模式只依赖 Pillow，不需要安装 PySide6。
"""

import argparse
import os
import signal
import sys
import threading

from app.enums.image_format import ImageFormat
from app.enums.rename_image_method import RenameImageMethod
from image_processor import ImageProcessor
from version import VERSION

_FORMAT_CHOICES = {
    'jpeg': ImageFormat.JPEG.value,
    'png': ImageFormat.PNG.value,
    'webp': ImageFormat.WEBP.value,
}
_RENAME_CHOICES = {
    'uuid': RenameImageMethod.UUID.value,
    'md5': RenameImageMethod.MD5.value,
    'number': RenameImageMethod.AUTO_INCREMENT_NUMBER.value,
}


class _ArgumentParser(argparse.ArgumentParser):
    """参数错误时返回退出码 1（argparse 默认是 2，会和“部分失败”的退出码冲突）。"""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, '%s: 错误: %s\n' % (self.prog, message))


def build_parser():
    parser = _ArgumentParser(
        prog='image-toolbox',
        description='图片工具箱命令行模式：批量转换格式、压缩、重命名图片。',
        epilog='退出码：0=全部成功，1=参数/运行错误，2=有图片失败或被跳过，3=处理被取消。',
    )
    parser.add_argument('-i', '--input', required=True, metavar='DIR', help='输入文件夹')
    parser.add_argument('-o', '--output', required=True, metavar='DIR', help='输出文件夹（不存在会自动创建）')
    parser.add_argument('-f', '--format', choices=sorted(_FORMAT_CHOICES), help='转换图片格式：jpeg / png / webp')
    parser.add_argument('-c', '--compress', type=float, metavar='KB', help='压缩图片到接近指定大小（KB），必须大于 0')
    parser.add_argument(
        '-r', '--rename', choices=sorted(_RENAME_CHOICES), help='重命名方式：uuid / md5 / number（自动递增序号）'
    )
    parser.add_argument('-R', '--recursive', action='store_true', help='递归处理子文件夹')
    parser.add_argument('-t', '--threads', type=int, default=4, metavar='N', help='处理线程数（1-128，默认 4）')
    parser.add_argument(
        '--alpha',
        choices=('white', 'black', 'skip', 'cancel'),
        default='white',
        help='透明图片转 JPEG 时的处理方式：white=合成白底（默认）/ black=合成黑底 / skip=跳过 / cancel=遇到时取消处理',
    )
    parser.add_argument(
        '--duplicate',
        choices=('rename', 'overwrite', 'custom', 'cancel'),
        default='rename',
        help='输出文件重名处理方式：rename=自动加序号（默认）/ overwrite=覆盖 / '
        'custom=自定义前缀 / cancel=遇到时取消处理',
    )
    parser.add_argument(
        '--duplicate-prefix', metavar='PREFIX', help='--duplicate custom 时使用的文件名前缀，例如 pic -> pic_1.png'
    )
    parser.add_argument('-q', '--quiet', action='store_true', help='只输出错误和最终结果')
    parser.add_argument('--version', action='version', version='图片工具箱 %s' % VERSION)
    return parser


def _prepare_directories(args):
    if not os.path.isdir(args.input):
        print('错误：输入文件夹不存在或不是文件夹: %s' % args.input, file=sys.stderr)
        return False

    if os.path.exists(args.output) and not os.path.isdir(args.output):
        print('错误：输出路径已存在且不是文件夹: %s' % args.output, file=sys.stderr)
        return False

    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
        except OSError as error:
            print('错误：无法创建输出文件夹 %s（%s）' % (args.output, error), file=sys.stderr)
            return False

    return True


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format is None and args.compress is None and args.rename is None:
        parser.error('至少指定一种处理方式：--format / --compress / --rename')
    if args.compress is not None and args.compress <= 0:
        parser.error('--compress 必须大于 0')
    if not 1 <= args.threads <= 128:
        parser.error('--threads 必须在 1-128 之间')
    if args.duplicate == 'custom' and not args.duplicate_prefix:
        parser.error('--duplicate custom 需要同时指定 --duplicate-prefix')

    if not _prepare_directories(args):
        return 1

    # Ctrl+C 第一次按下时优雅取消：当前图片处理完成后停止
    interrupted = threading.Event()
    previous_handler = signal.getsignal(signal.SIGINT)

    def handle_interrupt(*_args):
        if interrupted.is_set():
            raise KeyboardInterrupt
        interrupted.set()
        print('\n收到中断，正在取消（当前图片处理完成后停止）...', file=sys.stderr)

    signal.signal(signal.SIGINT, handle_interrupt)

    def console(message):
        if args.quiet and (
            message.startswith('正在') or message.startswith('处理完成') or message.startswith('处理已取消')
        ):
            return
        print(message, flush=True)

    def question_callback(question):
        if question.get('type') == 'alpha':
            return args.alpha
        if question.get('type') == 'duplicate':
            if args.duplicate == 'custom':
                return {'action': 'custom', 'prefix': args.duplicate_prefix}
            return args.duplicate
        return 'cancel'

    processor = ImageProcessor(
        args.input,
        args.output,
        recursive_load=args.recursive,
        is_selected_convert_image_format=args.format is not None,
        image_format=_FORMAT_CHOICES.get(args.format),
        is_selected_compress_image=args.compress is not None,
        image_target_size=args.compress,
        is_selected_rename_image=args.rename is not None,
        rename_image_method=_RENAME_CHOICES.get(args.rename),
        thread_count=args.threads,
        alpha_handling='ask',
        duplicate_handling='ask',
    )

    try:
        result = processor.run(
            console_callback=console,
            question_callback=question_callback,
            cancel_callback=interrupted.is_set,
        )
    except KeyboardInterrupt:
        print('处理被强制中断。', file=sys.stderr)
        return 3
    except Exception as error:
        print('处理失败: %s: %s' % (type(error).__name__, error), file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGINT, previous_handler)

    total_count = result.get('total', 0)
    success_count = result.get('success', 0)
    failed = result.get('failed') or []
    skipped_count = result.get('skipped', 0)

    if result.get('cancelled') is True:
        print('处理已取消：成功 %d 张，失败 %d 张。' % (success_count, len(failed)))
        return 3

    if result.get('aborted') is True:
        print('处理已中止：成功 %d 张，失败 %d 张。' % (success_count, len(failed)))
        return 3

    if total_count == 0:
        print('没有找到可以处理的图片。', file=sys.stderr)
        return 1

    print('处理完成：成功 %d 张，失败 %d 张。' % (success_count, len(failed)))
    if skipped_count > 0:
        print('其中 %d 张因透明通道被跳过。' % skipped_count)

    if failed:
        print('未成功处理的文件：', file=sys.stderr)
        for name in failed:
            print('  - %s' % name, file=sys.stderr)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
