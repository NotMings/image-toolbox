"""文件夹选择对话框的封装。"""

from PySide6.QtWidgets import QFileDialog

from app.i18n import tr


def select_folder(parent):
    """弹出文件夹选择对话框，返回选中的文件夹路径。"""
    return QFileDialog.getExistingDirectory(parent, tr('Select folder'), './')
