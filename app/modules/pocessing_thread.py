from PySide6.QtCore import (QThread, Signal)


class ProcessingThread(QThread):
    signal_result = Signal(object)
    signal_finished = Signal()

    signal_progress = Signal(int)
    signal_progress_count = Signal(int)
    signal_console = Signal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        result = self.func(
            *self.args,
            progress_callback=self.report_progress,
            progress_count_callback=self.report_progress_count,
            console_callback=self.report_console,
            **self.kwargs
        )
        # 任务完成后发出信号
        self.signal_result.emit(result)
        self.signal_finished.emit()

    def report_progress(self, progress):
        self.signal_progress.emit(progress)

    def report_progress_count(self, progress_count):
        self.signal_progress_count.emit(progress_count)

    def report_console(self, console):
        self.signal_console.emit(console)
