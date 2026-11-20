import threading

from PySide6.QtCore import (QThread, Signal)


class ProcessingThread(QThread):
    signal_result = Signal(object)
    signal_finished = Signal()

    signal_progress = Signal(int)
    signal_progress_count = Signal(int)
    signal_console = Signal(object)

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

    def run(self):
        try:
            result = self.func(
                *self.args,
                progress_callback=self.report_progress,
                progress_count_callback=self.report_progress_count,
                console_callback=self.report_console,
                pause_callback=self.check_point,
                **self.kwargs
            )
            # 任务完成后发出信号
            self.signal_result.emit(result)
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

    def abort(self):
        """中止处理：唤醒可能正在暂停等待的线程，并让处理循环尽快退出。"""
        with self._pause_condition:
            self._aborted = True
            self._paused = False
            self._pause_condition.notify_all()

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
