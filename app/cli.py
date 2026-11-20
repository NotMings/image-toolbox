#!/usr/bin/env python
"""Image Toolbox command line: batch convert, compress, and rename images.

The graphical interface and the command line share one program:
- no arguments: start the GUI
- with arguments: run in command-line mode (English only)

Command-line mode depends only on Pillow; PySide6 is not required.
"""

import argparse
import os
import re
import signal
import sys
import threading

from app.enums.image_format import ImageFormat
from app.enums.rename_image_method import RenameImageMethod
from app.i18n import set_language
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

# Routine progress lines hidden by --quiet.
_QUIET_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r'^Loading images\.\.\.',
        r'^Converting image format: .*',
        r'^Compressing image: .*',
        r'^Renaming image: .*',
        r'^Completed: .*',
        r'^Cancelled: .*',
    )
)


class _ArgumentParser(argparse.ArgumentParser):
    """Argument errors exit with code 1 (argparse defaults to 2, which means partial failure)."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, '%s: error: %s\n' % (self.prog, message))


def build_parser():
    parser = _ArgumentParser(
        prog='image-toolbox',
        description='Image Toolbox command line: batch convert, compress, and rename images.',
        epilog='Exit codes: 0=success, 1=argument/runtime error, 2=some images failed or were skipped, 3=cancelled.',
    )
    parser.add_argument('-i', '--input', required=True, metavar='DIR', help='input folder')
    parser.add_argument(
        '-o', '--output', required=True, metavar='DIR', help='output folder (created if it does not exist)'
    )
    parser.add_argument('-f', '--format', choices=sorted(_FORMAT_CHOICES), help='convert to jpeg / png / webp')
    parser.add_argument(
        '-c',
        '--compress',
        type=float,
        metavar='KB',
        help='compress images to approximately the given size in KB (must be > 0)',
    )
    parser.add_argument(
        '-r',
        '--rename',
        choices=sorted(_RENAME_CHOICES),
        help='rename method: uuid / md5 / number (auto-increment)',
    )
    parser.add_argument('-R', '--recursive', action='store_true', help='process subfolders recursively')
    parser.add_argument('-t', '--threads', type=int, default=4, metavar='N', help='worker threads (1-128, default 4)')
    parser.add_argument(
        '--alpha',
        choices=('white', 'black', 'skip', 'cancel'),
        default='white',
        help='transparent images to JPEG: white=flatten onto white (default) / black=flatten onto black / '
        'skip=skip / cancel=cancel on first occurrence',
    )
    parser.add_argument(
        '--duplicate',
        choices=('rename', 'overwrite', 'custom', 'cancel'),
        default='rename',
        help='duplicate output names: rename=auto-rename (default) / overwrite=overwrite / '
        'custom=custom prefix / cancel=cancel on first occurrence',
    )
    parser.add_argument(
        '--duplicate-prefix',
        metavar='PREFIX',
        help='filename prefix for --duplicate custom, e.g. pic -> pic_1.png',
    )
    parser.add_argument('-q', '--quiet', action='store_true', help='only output errors and the final result')
    parser.add_argument('--version', action='version', version='Image Toolbox %s' % VERSION)
    return parser


def _prepare_directories(args):
    if not os.path.isdir(args.input):
        print('Error: input folder does not exist or is not a folder: %s' % args.input, file=sys.stderr)
        return False

    if os.path.exists(args.output) and not os.path.isdir(args.output):
        print('Error: output path exists and is not a folder: %s' % args.output, file=sys.stderr)
        return False

    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
        except OSError as error:
            print('Error: cannot create output folder %s (%s)' % (args.output, error), file=sys.stderr)
            return False

    return True


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format is None and args.compress is None and args.rename is None:
        parser.error('specify at least one action: --format / --compress / --rename')
    if args.compress is not None and args.compress <= 0:
        parser.error('--compress must be greater than 0')
    if not 1 <= args.threads <= 128:
        parser.error('--threads must be between 1 and 128')
    if args.duplicate == 'custom' and not args.duplicate_prefix:
        parser.error('--duplicate custom requires --duplicate-prefix')

    if not _prepare_directories(args):
        return 1

    # Image processor logs follow the global GUI language; command line is always English.
    set_language('en')

    # First Ctrl+C requests a graceful cancel: finish the current image, then stop.
    interrupted = threading.Event()
    previous_handler = signal.getsignal(signal.SIGINT)

    def handle_interrupt(*_args):
        if interrupted.is_set():
            raise KeyboardInterrupt
        interrupted.set()
        print('\nInterrupted; cancelling after the current image finishes...', file=sys.stderr)

    signal.signal(signal.SIGINT, handle_interrupt)

    def console(message):
        if args.quiet and any(pattern.match(message) for pattern in _QUIET_PATTERNS):
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
        print('Processing was interrupted.', file=sys.stderr)
        return 3
    except Exception as error:
        print('Processing failed: %s: %s' % (type(error).__name__, error), file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGINT, previous_handler)

    total_count = result.get('total', 0)
    success_count = result.get('success', 0)
    failed = result.get('failed') or []
    skipped_count = result.get('skipped', 0)

    if result.get('cancelled') is True:
        print('Cancelled: %d succeeded, %d failed.' % (success_count, len(failed)))
        return 3

    if result.get('aborted') is True:
        print('Stopped: %d succeeded, %d failed.' % (success_count, len(failed)))
        return 3

    if total_count == 0:
        print('No processable images found.', file=sys.stderr)
        return 1

    print('Completed: %d succeeded, %d failed.' % (success_count, len(failed)))
    if skipped_count > 0:
        print('%d image(s) skipped because of transparency.' % skipped_count)

    if failed:
        print('Files not processed successfully:', file=sys.stderr)
        for name in failed:
            print('  - %s' % name, file=sys.stderr)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
