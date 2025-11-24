import json

from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QWidget
from typing import Optional, Any, Dict, Tuple, List


class ProcessWorker(QWidget):
    work_started = False
    cancelled = False
    stopped = False

    def __init__(self, process: Tuple[str, List[str]]):
        super().__init__()

        self.process_file_path = process[0]
        self.process_arguments = process[1]

        self.process: Optional[QProcess] = None
        self.start_process()

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
            self.cancelled = True
            self.process.kill()

    def start_work(self, cmd: Dict[str, Any]):
        if self.work_started:
            raise ValueError("Work already started")

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

            if "status" in msg:
                self.on_work_status(msg["status"])

            if "result" in msg:
                self.on_work_result(msg["result"])
                self.on_work_finished()
                self.work_started = False

            if "error" in msg:
                self.on_work_error(msg["error"])
                self.on_work_finished()
                self.work_started = False

    def on_stderr(self):
        err = self.process.readAllStandardError().data().decode()
        print(err)

    def on_process_error(self, error: QProcess.ProcessError):
        if self.work_started and not self.stopped and not self.cancelled:
            self.on_work_error(str(error))

    def on_process_finished(self):
        if not self.stopped:
            if self.work_started:
                self.on_work_finished()
                self.work_started = False

            if self.cancelled:
                self.start_process()
                self.cancelled = False

    def on_work_status(self, msg: str):
        pass

    def on_work_result(self, result: Any):
        pass

    def on_work_error(self, error: Any):
        pass

    def on_work_finished(self):
        pass

    def stop_process(self):
        self.stopped = True

        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(3000)
