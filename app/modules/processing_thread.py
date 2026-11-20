"""后台处理线程：在 QThread 中运行处理函数，并转发进度、日志、暂停/取消和询问状态。"""

import threading

from PySide6.QtCore import QThread, Signal

from app.i18n import tr


class ProcessingThread(QThread):
    """包装处理函数的工作线程。"""

    signal_result = Signal(object)
    signal_finished = Signal()

    signal_progress = Signal(int)
    signal_progress_count = Signal(int)
    signal_console = Signal(object)
    signal_error = Signal(str)
    signal_question = Signal(object)

    signal_paused = Signal()
    signal_resumed = Signal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

        # 暂停/恢复使用条件变量实现，暂停时处理线程会阻塞在 check_point 处
        self._pause_condition = threading.Condition()
        self._paused = False
        self._aborted = False

        # 需要用户选择时（如透明图片、输出重名），工作线程通过条件变量等待界面回答
        self._question_condition = threading.Condition()
        self._question_done = True
        self._question_answer = None

        # 取消请求：不再开始新图片，正在处理的图片会先完成
        self._cancel_event = threading.Event()

    def run(self):
        try:
            result = self.func(
                *self.args,
                progress_callback=self.report_progress,
                progress_count_callback=self.report_progress_count,
                console_callback=self.report_console,
                pause_callback=self.check_point,
                question_callback=self.ask_question,
                cancel_callback=self.is_cancel_requested,
                **self.kwargs,
            )
            # 任务完成后发出信号
            self.signal_result.emit(result)
        except Exception as error:
            # 把异常反馈到界面，避免出现"处理完成"但实际上失败的情况
            message = '%s: %s' % (type(error).__name__, error)
            self.signal_console.emit(tr('Processing error: %s') % message)
            self.signal_error.emit(message)
        finally:
            # 无论处理成功还是抛出异常，都通知界面恢复按钮状态
            self.signal_finished.emit()

    def pause(self):
        with self._pause_condition:
            if self._aborted:
                return
            self._paused = True
        self.signal_paused.emit()

    def resume(self):
        with self._pause_condition:
            if self._aborted:
                return
            self._paused = False
            self._pause_condition.notify_all()
        self.signal_resumed.emit()

    def request_cancel(self):
        """请求取消处理：不再开始新的图片，正在处理的图片会先处理完成。

        如果当前处于暂停状态，会自动恢复播放，否则正在处理的图片无法完成。
        """
        self._cancel_event.set()
        with self._pause_condition:
            self._paused = False
            self._pause_condition.notify_all()

    def is_cancel_requested(self):
        return self._cancel_event.is_set()

    def abort(self):
        """中止处理：唤醒可能正在暂停或等待用户回答的线程，并让处理循环尽快退出。"""
        with self._pause_condition:
            self._aborted = True
            self._paused = False
            self._pause_condition.notify_all()

        with self._question_condition:
            self._question_done = True
            self._question_answer = 'cancel'
            self._question_condition.notify_all()

    def ask_question(self, question):
        """在工作线程中向界面提问，并阻塞等待界面回答；中止时返回 None。"""
        with self._question_condition:
            if self._aborted:
                return None
            self._question_done = False
            self._question_answer = None

        self.signal_question.emit(question)

        with self._question_condition:
            while not self._question_done:
                self._question_condition.wait()
            return self._question_answer

    def answer_question(self, answer):
        """由界面线程调用，回答 ask_question 的提问。"""
        with self._question_condition:
            self._question_answer = answer
            self._question_done = True
            self._question_condition.notify_all()

    def is_paused(self):
        with self._pause_condition:
            return self._paused

    def check_point(self):
        """处理函数在每处理一步之前调用：暂停时阻塞当前线程，返回 False 表示应停止处理。"""
        with self._pause_condition:
            while self._paused and not self._aborted:
                self._pause_condition.wait()
            return not self._aborted

    def report_progress(self, progress):
        self.signal_progress.emit(progress)

    def report_progress_count(self, progress_count):
        self.signal_progress_count.emit(progress_count)

    def report_console(self, console):
        self.signal_console.emit(console)
