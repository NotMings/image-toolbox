"""图片工具箱图形界面实现。"""

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
)

from app.i18n import LANGUAGES, detect_system_language, get_language, set_language, tr
from app.modules.processing_thread import ProcessingThread
from app.modules.select_folder import select_folder
from image_processor import ImageProcessor
from ui.compiled.main_window import Ui_toolBoxMainWindow
from version import VERSION


class ToolBoxMainWindow(Ui_toolBoxMainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        # 启动时按系统语言选择界面语言；命令行模式不受影响
        set_language(detect_system_language())

        # 窗口状态（放在实例上，避免多个窗口共享类属性）
        self.input_folder = None
        self.output_folder = None

        self.is_selected_convert_image_format = False
        self.image_format = None

        self.is_selected_compress_image = False
        self.image_target_size = None

        self.is_selected_rename_image = False
        self.rename_image_method = None

        self.main_processing_thread = None
        self.last_result = None
        self.last_error = None
        self.is_closing = False

        # 需要用户选择时才询问；同一批次内记住选择，避免重复弹窗
        self.alpha_handling = 'ask'
        self.duplicate_handling = 'ask'
        self.duplicate_prefix = None

        self.setupUi(self)
        self.show()

        icon_path = (
            os.path.join(getattr(sys, '_MEIPASS', ''), 'assets/icon.png')
            if getattr(sys, 'frozen', False)
            else 'assets/icon.png'
        )
        self.setWindowIcon(QIcon(icon_path))

        # 输入输出文件夹
        self.inputFolderPushButton.clicked.connect(self.input_button_clicked)
        self.inputFolderlineEdit.textChanged.connect(self.input_folder_line_edit_changed)
        self.outputFolderPushButton.clicked.connect(self.output_button_clicked)
        self.outputFolderlineEdit.textChanged.connect(self.output_folder_line_edit_changed)
        self.openOutputFolderPushButton.clicked.connect(self.open_output_folder_push_button_clicked)

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

        # 控制台输出框
        self.consoleTextEdit.setReadOnly(True)

        # 开始按钮
        self.startProcessingPushButton.clicked.connect(self.start_processing)

        # 暂停/继续按钮
        self.pauseProcessingPushButton.setEnabled(False)
        self.pauseProcessingPushButton.clicked.connect(self.pause_processing)

        # 取消按钮
        self.cancelProcessingPushButton.setEnabled(False)
        self.cancelProcessingPushButton.clicked.connect(self.cancel_processing)

        # 线程数滑块与输入框双向同步
        self.threadCountSlider.valueChanged.connect(self.threadCountSpinBox.setValue)
        self.threadCountSpinBox.valueChanged.connect(self.threadCountSlider.setValue)

        # 关于按钮
        self.actionAbout.triggered.connect(self.about_button_clicked)

        # 语言菜单：只切换界面文案，不改变处理逻辑
        self._build_language_menu()
        self._apply_language()

    def _build_language_menu(self):
        self.languageMenu = QMenu(tr('Language'), self.menuBar)
        self.menuBar.insertMenu(self.menu.menuAction(), self.languageMenu)
        self._language_actions = {}
        for code in LANGUAGES:
            action = self.languageMenu.addAction('')
            action.setCheckable(True)
            action.triggered.connect(lambda checked=False, code=code: self.change_language(code))
            self._language_actions[code] = action

    def change_language(self, language):
        set_language(language)
        self._apply_language()

    def _apply_language(self):
        self.setWindowTitle(tr('Image Toolbox'))

        self.inputFolderlabel.setText(tr('Input folder'))
        self.inputFolderPushButton.setText(tr('Select folder'))
        self.recursiveloadingCheckBox.setText(tr('Load subfolders'))
        self.outputFolderlabel.setText(tr('Output folder'))
        self.outputFolderPushButton.setText(tr('Select folder'))
        self.openOutputFolderPushButton.setText(tr('Open output folder'))

        self.convertImageFormatCheckBox.setText(tr('Convert format'))
        self.compressImageCheckBox.setText(tr('Compress images'))
        self.renameImageCheckBox.setText(tr('Rename images'))
        self.renameImageComboBox.setItemText(2, tr('auto-increment number'))
        self.threadCountLabel.setText(tr('Threads'))
        self.threadCountSlider.setToolTip(tr('Drag to set thread count (1-128)'))
        self.threadCountSpinBox.setToolTip(tr('Enter thread count manually (1-128)'))
        self.totalProgresslabel.setText(tr('Progress'))

        if self.startProcessingPushButton.isEnabled():
            self.startProcessingPushButton.setText(tr('Start'))
        else:
            self.startProcessingPushButton.setText(tr('Processing...'))

        paused = self.main_processing_thread is not None and self.main_processing_thread.is_paused()
        if self.pauseProcessingPushButton.isEnabled():
            self.pauseProcessingPushButton.setText(tr('Resume') if paused else tr('Pause'))
        else:
            self.pauseProcessingPushButton.setText(tr('Pause'))

        cancelling = (
            self.main_processing_thread is not None
            and self.main_processing_thread.is_cancel_requested()
            and not self.cancelProcessingPushButton.isEnabled()
        )
        self.cancelProcessingPushButton.setText(tr('Cancelling...') if cancelling else tr('Cancel'))

        self.menu.setTitle(tr('Help'))
        self.actionAbout.setText(tr('About'))
        self.languageMenu.setTitle(tr('Language'))
        for code, action in self._language_actions.items():
            action.setText(tr(LANGUAGES[code]))
            action.setChecked(code == get_language())

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

    def open_output_folder_push_button_clicked(self):
        if self.output_folder is None or self.output_folder == '':
            QMessageBox.warning(self, tr('Warning'), tr('Please select an output folder'))
            return

        if not os.path.isdir(self.output_folder):
            QMessageBox.warning(self, tr('Warning'), tr('Output folder does not exist'))
            return

        try:
            os.startfile(self.output_folder)
        except OSError as error:
            QMessageBox.warning(self, tr('Warning'), tr('Failed to open output folder: %s') % error)

    def convert_image_format_check_box_clicked(self):
        if self.convertImageFormatCheckBox.isChecked() is True:
            self.convertImageFormatComboBox.setEnabled(True)

            default_index = 0 if self.image_format is None else self.image_format
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
            # 勾选时同步一次输入框的值，避免没改过数值时目标大小为 None
            self.image_target_size = self.compressImageDoubleSpinBox.value()
        else:
            self.compressImageDoubleSpinBox.setEnabled(False)
            self.is_selected_compress_image = False
            self.image_target_size = None

    def compress_image_double_spin_box_changed(self):
        self.image_target_size = self.compressImageDoubleSpinBox.value()

    def rename_image_check_box_clicked(self):
        if self.renameImageCheckBox.isChecked() is True:
            self.renameImageComboBox.setEnabled(True)

            default_index = 0 if self.rename_image_method is None else self.rename_image_method
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
        if self.input_folder is None or self.input_folder == '':
            QMessageBox.warning(self, tr('Warning'), tr('Please select an input folder'))
            return

        if not os.path.isdir(self.input_folder):
            QMessageBox.warning(self, tr('Warning'), tr('Input folder does not exist. Please choose again'))
            return

        if self.output_folder is None or self.output_folder == '':
            QMessageBox.warning(self, tr('Warning'), tr('Please select an output folder'))
            return

        if not os.path.isdir(self.output_folder):
            QMessageBox.warning(self, tr('Warning'), tr('Output folder does not exist. Please choose again'))
            return

        if self.image_format is None and self.image_target_size is None and self.rename_image_method is None:
            QMessageBox.warning(self, tr('Warning'), tr('Select at least one action'))
            return

        if self.is_selected_compress_image is True and (self.image_target_size is None or self.image_target_size <= 0):
            QMessageBox.warning(self, tr('Warning'), tr('Compression target size must be greater than 0'))
            return

        self.last_result = None
        self.last_error = None
        self.alpha_handling = 'ask'
        self.duplicate_handling = 'ask'
        self.duplicate_prefix = None

        self.startProcessingPushButton.setEnabled(False)
        self.startProcessingPushButton.setText(tr('Processing...'))
        self._set_thread_controls_enabled(False)

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
            alpha_handling=self.alpha_handling,
            duplicate_handling=self.duplicate_handling,
            thread_count=self.threadCountSpinBox.value(),
        )

        self.main_processing_thread = ProcessingThread(image_processor.run)
        self.main_processing_thread.signal_progress_count.connect(self.totalProgressBar.setMaximum)
        self.main_processing_thread.signal_progress.connect(self.totalProgressBar.setValue)
        self.main_processing_thread.signal_console.connect(self.consoleTextEdit.append)
        self.main_processing_thread.signal_result.connect(self.processing_result)
        self.main_processing_thread.signal_error.connect(self.processing_error)
        self.main_processing_thread.signal_question.connect(self.handle_question)
        self.main_processing_thread.signal_finished.connect(self.processing_finished)
        self.main_processing_thread.start()

        self.pauseProcessingPushButton.setEnabled(True)
        self.pauseProcessingPushButton.setText(tr('Pause'))
        self.cancelProcessingPushButton.setEnabled(True)
        self.cancelProcessingPushButton.setText(tr('Cancel'))

    def _set_thread_controls_enabled(self, enabled):
        self.threadCountSlider.setEnabled(enabled)
        self.threadCountSpinBox.setEnabled(enabled)

    def pause_processing(self):
        if self.main_processing_thread is None or not self.main_processing_thread.isRunning():
            return

        if self.main_processing_thread.is_paused():
            self.main_processing_thread.resume()
            self.pauseProcessingPushButton.setText(tr('Pause'))
            self.consoleTextEdit.append(tr('Resuming'))
        else:
            self.main_processing_thread.pause()
            self.pauseProcessingPushButton.setText(tr('Resume'))
            self.consoleTextEdit.append(tr('Paused. Click "Resume" to continue.'))

    def cancel_processing(self):
        if self.main_processing_thread is None or not self.main_processing_thread.isRunning():
            return

        if self.main_processing_thread.is_cancel_requested():
            return

        self.main_processing_thread.request_cancel()
        self.cancelProcessingPushButton.setEnabled(False)
        self.cancelProcessingPushButton.setText(tr('Cancelling...'))
        # 取消时需要让正在处理的图片完成，因此暂停状态会被自动恢复
        self.pauseProcessingPushButton.setEnabled(False)
        self.pauseProcessingPushButton.setText(tr('Pause'))
        self.consoleTextEdit.append(tr('Cancelling; waiting for the current image to finish...'))

    def processing_result(self, result):
        self.last_result = result

    def processing_error(self, message):
        self.last_error = message

    def handle_question(self, request):
        """处理工作线程的提问（透明图片 / 输出重名），并把选择结果回传给线程。"""
        if self.is_closing is True:
            self.answer_question('cancel')
            return

        question_type = request.get('type')

        if question_type == 'alpha':
            if self.alpha_handling != 'ask':
                answer = self.alpha_handling
            else:
                answer = self.ask_alpha_handling(request)
                if answer in ('white', 'skip'):
                    self.alpha_handling = answer
        elif question_type == 'duplicate':
            if self.duplicate_handling == 'overwrite':
                answer = 'overwrite'
            elif self.duplicate_handling == 'rename':
                answer = 'rename'
            elif self.duplicate_handling == 'custom' and self.duplicate_prefix:
                answer = {'action': 'custom', 'prefix': self.duplicate_prefix}
            else:
                answer = self.ask_duplicate_handling(request)
                if answer in ('overwrite', 'rename'):
                    self.duplicate_handling = answer
                elif isinstance(answer, dict) and answer.get('action') == 'custom':
                    self.duplicate_handling = 'custom'
                    self.duplicate_prefix = answer.get('prefix')
        else:
            answer = 'cancel'

        self.answer_question(answer)

    def answer_question(self, answer):
        if self.main_processing_thread is not None:
            self.main_processing_thread.answer_question(answer)

    def ask_alpha_handling(self, request):
        box = QMessageBox(self)
        box.setWindowTitle(tr('Transparent image'))
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(
            tr(
                'Image "%s" contains transparency, but JPEG does not support it.\n'
                'Choose how to handle it (applies to the rest of this batch):'
            )
            % request.get('source_name', '')
        )
        white_button = box.addButton(tr('Flatten onto white'), QMessageBox.ButtonRole.AcceptRole)
        skip_button = box.addButton(tr('Skip this image'), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(tr('Cancel processing'), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(white_button)
        box.exec()

        clicked = box.clickedButton()
        if clicked is white_button:
            return 'white'
        if clicked is skip_button:
            return 'skip'
        return 'cancel'

    def ask_duplicate_handling(self, request):
        desired_name = request.get('desired_name', '')
        if request.get('in_batch') is True:
            reason = tr('The name "%s" duplicates a file already produced in this batch') % desired_name
        else:
            reason = tr('A file named "%s" already exists in the output folder') % desired_name

        box = QMessageBox(self)
        box.setWindowTitle(tr('Duplicate filename'))
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(reason + tr('.\nChoose how to handle it (applies to the rest of this batch):'))
        overwrite_button = box.addButton(tr('Overwrite'), QMessageBox.ButtonRole.DestructiveRole)
        rename_button = box.addButton(tr('Auto-rename'), QMessageBox.ButtonRole.AcceptRole)
        custom_button = box.addButton(tr('Custom prefix'), QMessageBox.ButtonRole.ActionRole)
        box.addButton(tr('Cancel processing'), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(rename_button)
        box.exec()

        clicked = box.clickedButton()
        if clicked is overwrite_button:
            return 'overwrite'
        if clicked is rename_button:
            return 'rename'
        if clicked is custom_button:
            prefix, accepted = QInputDialog.getText(
                self,
                tr('Custom filename prefix'),
                tr('Enter a prefix (duplicates become prefix_1.png, prefix_2.png, ...):'),
                text='img',
            )
            if accepted and prefix.strip():
                return {'action': 'custom', 'prefix': prefix.strip()}
            return 'rename'
        return 'cancel'

    def processing_finished(self):
        self.startProcessingPushButton.setEnabled(True)
        self.startProcessingPushButton.setText(tr('Start'))
        self.pauseProcessingPushButton.setEnabled(False)
        self.pauseProcessingPushButton.setText(tr('Pause'))
        self.cancelProcessingPushButton.setEnabled(False)
        self.cancelProcessingPushButton.setText(tr('Cancel'))
        self._set_thread_controls_enabled(True)

        # 关闭窗口时线程被中止，不再弹出提示框
        if self.is_closing is True:
            return

        if self.last_error is not None:
            QMessageBox.warning(self, tr('Warning'), tr('Processing failed: %s') % self.last_error)
            return

        result = self.last_result or {}
        total_count = result.get('total', 0)
        success_count = result.get('success', 0)
        failed = result.get('failed') or []
        skipped_count = result.get('skipped', 0)

        if result.get('cancelled') is True:
            message = tr('Cancelled: %d succeeded, %d failed.') % (success_count, len(failed))
            if failed:
                message += '\n' + tr('Failed files were skipped; see the console for details.')
            if skipped_count > 0:
                message += '\n' + tr('%d image(s) skipped because of transparency.') % skipped_count
            QMessageBox.information(self, 'Information', message)
        elif result.get('aborted') is True:
            QMessageBox.information(self, tr('Information'), tr('Processing stopped'))
        elif total_count == 0:
            QMessageBox.information(self, tr('Information'), tr('No processable images found'))
        elif failed:
            message = (
                tr('Completed: %d succeeded, %d failed.') % (success_count, len(failed))
                + '\n'
                + tr('Failed files were skipped; see the console for details.')
            )
            if skipped_count > 0:
                message += '\n' + tr('%d image(s) skipped because of transparency.') % skipped_count
            QMessageBox.warning(self, tr('Warning'), message)
        else:
            QMessageBox.information(self, tr('Information'), tr('Completed: %d images') % success_count)

    def closeEvent(self, event):
        self.is_closing = True

        # 窗口关闭时中止可能仍在运行（甚至处于暂停状态）的处理线程，避免进程无法退出
        if self.main_processing_thread is not None and self.main_processing_thread.isRunning():
            self.main_processing_thread.abort()
            self.main_processing_thread.wait()
        super().closeEvent(event)

    def about_button_clicked(self):
        free_software_text = tr(
            'This software is free. If you paid for it through another channel, '
            'please request a refund and report the seller.'
        )
        QMessageBox.about(
            self,
            tr('About'),
            '<div>'
            '<h1>IMAGE TOOlBOX</h1>'
            f'<p>{tr("Version")}: {VERSION}</p>'
            f'<p>{tr("Author")}: {tr("Unknown")}</p>'
            f'<p>{tr("GitHub Link")}: '
            '<a href="https://github.com/notmings/image-toolbox">https://github.com/notmings/image-toolbox</a>'
            '</p>'
            f'<p>{free_software_text}</p>'
            '</div>',
        )


def run():
    """启动图形界面，返回 QApplication 的退出码。"""
    app = QApplication(sys.argv)
    _window = ToolBoxMainWindow()
    return app.exec()
