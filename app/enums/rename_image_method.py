"""重命名方式枚举（值需与界面下拉框顺序保持一致）。"""

from enum import Enum


class RenameImageMethod(Enum):
    UUID = 0
    MD5 = 1
    AUTO_INCREMENT_NUMBER = 2
