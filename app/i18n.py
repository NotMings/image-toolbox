"""多语言支持（基于 Python 标准库 gettext）。

图形界面启动时按系统语言自动选择：简体中文 / 繁体中文，其他语言默认英文；
用户也可以在「语言」菜单中手动切换。命令行模式固定使用英文。
"""

import gettext
import sys
from pathlib import Path

LANGUAGES = {
    'zh_CN': 'Simplified Chinese',
    'zh_TW': 'Traditional Chinese',
    'en': 'English',
}

# 源字符串是英文；DEFAULT_LANGUAGE 是系统语言不支持时的回退语言。
SOURCE_LANGUAGE = 'en'
DEFAULT_LANGUAGE = 'en'
DOMAIN = 'image_toolbox'


def _find_locale_dir():
    """返回翻译文件目录：源码运行用项目目录，打包后优先用 PyInstaller 解包目录。"""
    module_dir = Path(__file__).resolve().parent
    candidates = []
    if getattr(sys, 'frozen', False):
        base = Path(getattr(sys, '_MEIPASS', module_dir))
        candidates.append(base / 'app' / 'locales')
    candidates.append(module_dir / 'locales')
    candidates.append(Path.cwd() / 'app' / 'locales')
    for candidate in candidates:
        if candidate.is_dir():
            return str(candidate)
    return str(module_dir / 'locales')


_LOCALE_DIR = _find_locale_dir()


def _load_translation(code):
    if code == SOURCE_LANGUAGE:
        return gettext.NullTranslations()
    return gettext.translation(
        DOMAIN,
        localedir=_LOCALE_DIR,
        languages=[code],
        fallback=True,
    )


_current_language = DEFAULT_LANGUAGE
_translation = _load_translation(DEFAULT_LANGUAGE)


def language_from_locale(locale_name):
    """把系统语言标识（如 zh-CN、zh-Hant-TW、en-US）映射到支持的语言代码。"""
    name = (locale_name or '').replace('-', '_').lower()
    if name.startswith('zh'):
        if any(part in name for part in ('tw', 'hk', 'mo', 'hant')):
            return 'zh_TW'
        return 'zh_CN'
    return DEFAULT_LANGUAGE


def detect_system_language():
    """检测系统语言；检测失败或不支持时返回英文。"""
    # noinspection PyBroadException
    try:
        if sys.platform == 'win32':
            import ctypes

            buffer = ctypes.create_unicode_buffer(85)
            length = ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, 85)
            if length:
                return language_from_locale(buffer.value)
    except Exception:
        pass

    # noinspection PyBroadException
    try:
        import locale

        name = locale.getlocale()[0]
    except Exception:
        name = None
    return language_from_locale(name)


def set_language(code):
    """设置当前语言，非法值时保持原语言并返回当前语言。"""
    global _current_language, _translation
    if code not in LANGUAGES:
        return _current_language

    _current_language = code
    _translation = _load_translation(code)
    return _current_language


def get_language():
    """返回当前语言代码。"""
    return _current_language


def tr(text):
    """翻译文本；没有对应翻译时回退到英文源文本。"""
    return _translation.gettext(text)
