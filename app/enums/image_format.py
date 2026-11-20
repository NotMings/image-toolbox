"""图片格式枚举（值需与界面下拉框顺序保持一致）。"""

from enum import Enum


class ImageFormat(Enum):
    JPEG = 0
    PNG = 1
    WEBP = 2
