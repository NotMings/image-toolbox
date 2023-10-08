import os
import sys
import tempfile

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
)

from app.modules.pocessing_thread import ProcessingThread
from app.modules.select_folder import select_folder
from image_processor import ImageProcessor
from ui.compiled.main_window import Ui_toolBoxMainWindow


class ToolBoxMainWindow(Ui_toolBoxMainWindow, QMainWindow):
    input_folder = None
    output_folder = None
    temp_folder = tempfile.mkdtemp()

    is_selected_convert_image_format = False
    image_format = None

    is_selected_compress_image = False
    image_target_size = None

    is_selected_rename_image = False
    rename_image_method = None

    main_processing_thread = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        icon_path = os.path.join(sys._MEIPASS, 'assets/icon.png') if getattr(sys, 'frozen', False) else 'assets/icon.png'
        self.setWindowIcon(QIcon(icon_path))

        # 输入输出文件夹
        self.inputFolderPushButton.clicked.connect(self.input_button_clicked)
        self.inputFolderlineEdit.textChanged.connect(self.input_folder_line_edit_changed)
        self.outputFolderPushButton.clicked.connect(self.output_button_clicked)
        self.outputFolderlineEdit.textChanged.connect(self.output_folder_line_edit_changed)

        # 图片格式化
        self.convertImageFormatCheckBox.clicked.connect(self.convert_image_format_check_box_clicked)
        self.convertImageFormatComboBox.setEnabled(False)
        self.convertImageFormatComboBox.currentIndexChanged.connect(self.convert_image_format_combo_box_changed)

        # 图片压缩
        self.compressImageCheckBox.clicked.connect(self.compress_image_check_box_clicked)
        self.compressImageDoubleSpinBox.setEnabled(False)
        self.compressImageDoubleSpinBox.valueChanged.connect(self.compress_image_double_spin_box_changed)

        # 重命名
        self.renameImageCheckBox.clicked.connect(self.rename_image_check_box_clicked)
        self.renameImageComboBox.setEnabled(False)
        self.renameImageComboBox.currentIndexChanged.connect(self.rename_image_combo_box_changed)

        # 开始按钮
        self.startProcessingPushButton.clicked.connect(self.start_processing)

        # 关于按钮
        self.actionAbout.triggered.connect(self.about_button_clicked)

    def input_button_clicked(self):
        self.input_folder = select_folder(self)
        if self.input_folder is not None:
            self.inputFolderlineEdit.setText(self.input_folder)

    def input_folder_line_edit_changed(self):
        self.input_folder = self.inputFolderlineEdit.text()

    def output_button_clicked(self):
        self.output_folder = select_folder(self)
        if self.output_folder is not None:
            self.outputFolderlineEdit.setText(self.output_folder)

    def output_folder_line_edit_changed(self):
        self.output_folder = self.outputFolderlineEdit.text()

    def convert_image_format_check_box_clicked(self):
        if self.convertImageFormatCheckBox.isChecked() is True:
            self.convertImageFormatComboBox.setEnabled(True)

            default_index = 0
            self.convertImageFormatComboBox.setCurrentIndex(default_index)
            self.image_format = default_index
            self.is_selected_convert_image_format = True
        else:
            self.convertImageFormatComboBox.setEnabled(False)
            self.image_format = None
            self.is_selected_convert_image_format = False

    def convert_image_format_combo_box_changed(self):
        self.image_format = self.convertImageFormatComboBox.currentIndex()

    def compress_image_check_box_clicked(self):
        if self.compressImageCheckBox.isChecked() is True:
            self.compressImageDoubleSpinBox.setEnabled(True)
            self.is_selected_compress_image = True
        else:
            self.compressImageDoubleSpinBox.setEnabled(False)
            self.is_selected_compress_image = False

    def compress_image_double_spin_box_changed(self):
        self.image_target_size = self.compressImageDoubleSpinBox.value()

    def rename_image_check_box_clicked(self):
        if self.renameImageCheckBox.isChecked() is True:
            self.renameImageComboBox.setEnabled(True)

            default_index = 0
            self.renameImageComboBox.setCurrentIndex(default_index)
            self.rename_image_method = default_index
            self.is_selected_rename_image = True
        else:
            self.renameImageComboBox.setEnabled(False)
            self.rename_image_method = None
            self.is_selected_rename_image = False

    def rename_image_combo_box_changed(self):
        self.rename_image_method = self.renameImageComboBox.currentIndex()

    def start_processing(self):
        if self.input_folder is None:
            QMessageBox.warning(self, 'Warning', '请选择输入文件夹')
            return

        if self.output_folder is None:
            QMessageBox.warning(self, 'Warning', '请选择输出文件夹')
            return

        if self.image_format is None and self.image_target_size is None and self.rename_image_method is None:
            QMessageBox.warning(self, 'Warning', '至少选择一个处理方式')
            return

        if self.image_target_size is not None and self.image_target_size <= 0:
            QMessageBox.warning(self, 'Warning', '压缩图片大小必须大于0')
            return

        self.startProcessingPushButton.setEnabled(False)
        self.startProcessingPushButton.setText('正在处理...')

        recursive = False
        if self.recursiveloadingCheckBox.isChecked() is True:
            recursive = True

        image_processor = ImageProcessor(
            self.input_folder,
            self.output_folder,
            recursive_load=recursive,
            is_selected_convert_image_format=self.is_selected_convert_image_format,
            image_format=self.image_format,
            is_selected_compress_image=self.is_selected_compress_image,
            image_target_size=self.image_target_size,
            is_selected_rename_image=self.is_selected_rename_image,
            rename_image_method=self.rename_image_method,
        )

        self.main_processing_thread = ProcessingThread(image_processor.run)
        self.main_processing_thread.signal_progress_count.connect(self.totalProgressBar.setMaximum)
        self.main_processing_thread.signal_progress.connect(self.totalProgressBar.setValue)
        self.main_processing_thread.signal_console.connect(self.consoleTextEdit.append)
        self.main_processing_thread.signal_finished.connect(self.processing_finished)
        self.main_processing_thread.start()

    def processing_finished(self):
        self.startProcessingPushButton.setEnabled(True)
        self.startProcessingPushButton.setText('开始')
        QMessageBox.information(self, 'Information', '处理完成')

    def about_button_clicked(self):
        QMessageBox.about(
            self,
            'About',
            '<div>'
            '<h1>IMAGE TOOlBOX</h1>'
            '<p>Version: 1.1.0</p>'
            '<p>Author: 不明</p>'
            '<p>GitHub Link: '
            '<a href="https://github.com/notmings/image-toolbox">https://github.com/notmings/image-toolbox</a>'
            '</p>'
            '<p>此软件是免费软件，如果您通过其他渠道付费获取此软件，请立即退款并投诉相应商家</p>'
            '</div>'
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    toolBoxMainWindow = ToolBoxMainWindow()
    sys.exit(app.exec())
