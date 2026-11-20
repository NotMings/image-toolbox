#!/usr/bin/env python
"""把 app/locales 下的 .po 翻译编译成 gettext 使用的 .mo 文件。

用法：
    python tools/build_catalogs.py
"""

import ast
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / 'app' / 'locales'
DOMAIN = 'image_toolbox'


def _decode_string(line):
    """解析 .po 中一行带引号的字符串（支持转义）。"""
    return ast.literal_eval(line.strip())


def parse_po(path):
    """解析单个 .po 文件，返回 {msgid: msgstr}，包含文件头（msgid 为空）。"""
    text = path.read_text(encoding='utf-8')
    entries = {}

    for block in text.split('\n\n'):
        msgid_parts = []
        msgstr_parts = []
        target = None

        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('msgid '):
                target = msgid_parts
                target.append(_decode_string(line[len('msgid ') :]))
            elif line.startswith('msgstr '):
                target = msgstr_parts
                target.append(_decode_string(line[len('msgstr ') :]))
            elif line.startswith('"') and target is not None:
                target.append(_decode_string(line))

        msgid = ''.join(msgid_parts)
        msgstr = ''.join(msgstr_parts)
        if msgid or msgstr:
            entries[msgid] = msgstr

    return entries


def write_mo(entries, path):
    """按 GNU mo 格式写出翻译目录。"""
    catalog = {key: value for key, value in entries.items() if value}
    if '' not in catalog:
        raise ValueError('%s 缺少 gettext 文件头（msgid ""）' % path)

    keys = sorted(catalog)
    key_blob = b''
    value_blob = b''
    key_offsets = []
    value_offsets = []

    for key in keys:
        key_bytes = key.encode('utf-8')
        value_bytes = catalog[key].encode('utf-8')
        key_offsets.append((len(key_bytes), len(key_blob)))
        key_blob += key_bytes + b'\x00'
        value_offsets.append((len(value_bytes), len(value_blob)))
        value_blob += value_bytes + b'\x00'

    count = len(keys)
    original_table_offset = 28
    translated_table_offset = original_table_offset + 8 * count
    data_offset = translated_table_offset + 8 * count
    translated_data_offset = data_offset + len(key_blob)

    header = struct.pack(
        '<7I',
        0x950412DE,  # magic
        0,  # version
        count,
        original_table_offset,
        translated_table_offset,
        0,  # hash table size
        0,  # hash table offset
    )
    original_table = b''.join(struct.pack('<2I', length, data_offset + offset) for length, offset in key_offsets)
    translated_table = b''.join(
        struct.pack('<2I', length, translated_data_offset + offset) for length, offset in value_offsets
    )

    path.write_bytes(header + original_table + translated_table + key_blob + value_blob)


def main():
    compiled = 0
    for po_path in sorted(LOCALES_DIR.glob('*/LC_MESSAGES/*.po')):
        mo_path = po_path.with_suffix('.mo')
        if mo_path.name != DOMAIN + '.mo':
            continue
        write_mo(parse_po(po_path), mo_path)
        compiled += 1
        print('compiled:', mo_path.relative_to(ROOT))
    if compiled == 0:
        raise SystemExit('没有找到可编译的 .po 文件')
    print('完成，共编译 %d 个翻译文件。' % compiled)


if __name__ == '__main__':
    main()
