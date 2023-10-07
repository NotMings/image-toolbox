from PySide6.QtWidgets import QFileDialog


def select_folder(parent):
    return QFileDialog.getExistingDirectory(parent, '选择文件夹', './')

