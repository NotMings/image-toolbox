"""扫描文件夹中的图片文件。"""

import os

from PIL import Image


def _is_image_file(path):
    """尝试打开图片来识别文件类型，同时关闭文件句柄，避免扫描大文件夹时句柄泄漏。"""
    # 扫描阶段无法打开的文件一律跳过，避免单个坏文件中断整批处理
    # noinspection PyBroadException
    try:
        with Image.open(path):
            pass
        return True
    except Exception:
        return False


def load_image_path_from_folder(folder, recursive=False, check_point=None):
    """扫描文件夹中的图片文件。

    check_point: 可选的暂停/中止回调，返回 False 时立即停止扫描并返回 None。
    """
    if not os.path.isdir(folder):
        raise NotADirectoryError('输入路径不是文件夹: ' + folder)

    if recursive:
        file_paths = []
        for subdir, dirs, files in os.walk(folder):
            dirs.sort()
            for file in sorted(files):
                file_paths.append(os.path.join(subdir, file))
    else:
        file_paths = [os.path.join(folder, file) for file in sorted(os.listdir(folder))]

    image_path = []
    for path in file_paths:
        if check_point is not None and not check_point():
            return None
        if _is_image_file(path):
            image_path.append(path)

    return image_path
