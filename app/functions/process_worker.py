import json

from PySide6.QtCore import QProcess, Signal, QObject
from typing import Optional, Any, Dict, Tuple, List


class ProcessWorker(QObject):
    workStatus = Signal(str)
    workResult = Signal(object)
    workError = Signal(str)
    workFinished = Signal()

    process: Optional[QProcess] = None

    work_started = False
    work_cancelled = False
    work_error_msg = ""
    process_stopped = False

    def __init__(self, process: Tuple[str, List[str]]):
        super().__init__()

        self.process_file_path = process[0]
        self.process_arguments = process[1]

    def start_process(self):
        if not self.process or self.process.state() == QProcess.ProcessState.NotRunning:
            if self.process:
                self.process.deleteLater()

            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.on_stdout)
            self.process.readyReadStandardError.connect(self.on_stderr)
            self.process.errorOccurred.connect(self.on_process_error)
            self.process.finished.connect(self.on_process_finished)

            self.process.start(self.process_file_path, self.process_arguments)

    def cancel_work(self):
        if self.process:
            self.work_cancelled = True
            self.process.kill()

    def start_work(self, cmd: Dict[str, Any]):
        if self.work_started:
            raise RuntimeError("Work already started")

        self.work_started = True

        self.start_process()

        line = json.dumps(cmd) + "\n"
        self.process.write(line.encode("utf-8"))

    def on_stdout(self):
        while self.process.canReadLine():
            line = self.process.readLine().data().decode().strip()

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                print(line)
                continue

            if not isinstance(msg, dict):
                print(line)
                continue

            if "status" in msg:
                self.workStatus.emit(msg["status"])

            if "result" in msg:
                self.workResult.emit(msg["result"])
                self._set_work_finished()

            if "error" in msg:
                self.workError.emit(msg["error"])
                self._set_work_finished()

    def on_stderr(self):
        err = self.process.readAllStandardError().data().decode()
        self.work_error_msg += err

    def on_process_error(self, error: QProcess.ProcessError):
        if self.work_started and not self.process_stopped and not self.work_cancelled:
            self.workError.emit(str(error))

    def on_process_finished(self):
        if not self.process_stopped:
            if self.work_started:
                if not self.work_cancelled:
                    error_msg = self.work_error_msg if self.work_error_msg is not None else "Process finished before outputting result"
                    self.workError.emit(error_msg)

                self._set_work_finished()

            if self.work_cancelled:
                self.start_process()
                self.work_cancelled = False

    def stop_process(self):
        self.process_stopped = True

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(3000)

    def _set_work_finished(self):
        self.workFinished.emit()
        self.work_started = False
        self.work_error_msg = ""
