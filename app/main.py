import os
import sys
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

from PySide6 import QtCore, QtWidgets


class AnalysisWorker(QtCore.QThread):
    progress_changed = QtCore.Signal(int)
    status_changed = QtCore.Signal(str)
    completed = QtCore.Signal(str)
    failed = QtCore.Signal(str)

    def __init__(self, audio_file_path: str, parent=None) -> None:
        super().__init__(parent)
        self.audio_file_path = audio_file_path

    def _ensure_paths(self) -> None:
        # Resolve base dir (supports PyInstaller via _MEIPASS)
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        project_root = base_dir

        # Ensure scripts are importable
        scripts_dir = project_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        # Set CWD to scripts so '../models/...' resolves correctly
        if scripts_dir.exists():
            os.chdir(scripts_dir)

        # Prepend ffmpeg dir if bundled
        ffmpeg_dir = project_root / "app" / "resources" / "ffmpeg" / "darwin-arm64"
        if ffmpeg_dir.exists():
            os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")

    def _probe_duration_seconds(self, file_path: str) -> float:
        # Prefer ffprobe to avoid loading the file in memory
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=nokey=1:noprint_wrappers=1",
                    file_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )
            return float(result.stdout.strip())
        except Exception:
            # Fallback to librosa if ffprobe not available
            import librosa

            return float(librosa.get_duration(path=file_path))

    def _extract_chunk_with_ffmpeg(self, src_path: str, start_time_s: float, duration_s: float, dst_wav_path: str) -> None:
        # Create a 1-channel 48k WAV for consistent downstream processing
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-ss",
            str(start_time_s),
            "-i",
            src_path,
            "-t",
            str(duration_s),
            "-ac",
            "1",
            "-ar",
            "48000",
            "-vn",
            "-sn",
            dst_wav_path,
        ]
        subprocess.run(cmd, check=True)

    def run(self) -> None:
        try:
            self._ensure_paths()

            # Lazy imports after path setup
            from classifier import Classifier
            from run_model import process_audio_segment
            import functions

            # After chdir above, project_root remains the base path
            project_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))

            # Resource paths
            keras_model_path = project_root / "models" / "model_v3_5.keras"
            classes_csv_path = project_root / "scripts" / "classes.csv"
            calibration_path = project_root / "scripts" / "Pred_adjustment" / "calibration_params.npy"

            if not keras_model_path.exists():
                raise FileNotFoundError(f"Missing model file: {keras_model_path}")
            if not classes_csv_path.exists():
                raise FileNotFoundError(f"Missing classes file: {classes_csv_path}")
            if not calibration_path.exists():
                raise FileNotFoundError(f"Missing calibration file: {calibration_path}")

            # Default parameters for MVP
            threshold = 0.5
            include_sdm = False
            include_noise = False
            overlap = 1.0
            chunk_size_s = 600

            # Metadata
            file_name = os.path.basename(self.audio_file_path)
            doy_from_name = functions.get_day_of_year_from_filename(file_name)
            day_of_year = doy_from_name if doy_from_name is not None else datetime.now().timetuple().tm_yday

            # Load models and tables
            tflite_threads = max(1, os.cpu_count() or 1)
            classifier = Classifier(
                path_to_mlk_model=str(keras_model_path),
                sr=48000,
                clip_dur=3.0,
                TFLITE_THREADS=tflite_threads,
                offset=0,
                dur=0,
            )
            species_name_list = pd.read_csv(classes_csv_path)
            calibration_params = np.load(calibration_path)
            migration_params = np.array([])  # Unused when include_sdm=False

            # Output file
            output_dir = os.path.dirname(self.audio_file_path)
            output_file_path, _exists = functions.make_output_file_path(output_dir, file_name)
            with open(output_file_path, "w") as f:
                f.write("Start (s),End (s),Scientific name,Common name,Confidence\n")

            # Determine duration and iterate chunks
            total_duration = self._probe_duration_seconds(self.audio_file_path)
            total_chunks = int(np.ceil(total_duration / chunk_size_s)) if total_duration > 0 else 1

            self.status_changed.emit("Starting analysis...")

            with tempfile.TemporaryDirectory() as temp_dir:
                processed_chunks = 0
                start_time = 0.0

                while start_time < total_duration:
                    seg_duration = min(chunk_size_s, total_duration - start_time)
                    temp_wav = os.path.join(temp_dir, f"chunk_{int(start_time)}.wav")

                    # Extract chunk
                    self._extract_chunk_with_ffmpeg(self.audio_file_path, start_time, seg_duration, temp_wav)

                    # Process chunk
                    results_df = process_audio_segment(
                        temp_wav,
                        classifier,
                        calibration_params,
                        threshold,
                        include_sdm,
                        include_noise,
                        migration_params,
                        0.0,  # lat (unused)
                        0.0,  # lon (unused)
                        day_of_year,
                        species_name_list,
                        start_time,
                        overlap,
                    )

                    if results_df is not None and not results_df.empty:
                        # Map to expected CSV column names
                        results_df = results_df.rename(
                            columns={
                                "start_time": "Start (s)",
                                "end_time": "End (s)",
                                "scientific_name": "Scientific name",
                                "common_name": "Common name",
                                "confidence": "Confidence",
                            }
                        )
                        results_df = results_df[[
                            "Start (s)",
                            "End (s)",
                            "Scientific name",
                            "Common name",
                            "Confidence",
                        ]]
                        results_df.to_csv(output_file_path, mode="a", header=False, index=False)

                    processed_chunks += 1
                    progress = int((processed_chunks / total_chunks) * 100)
                    self.progress_changed.emit(progress)
                    self.status_changed.emit(
                        f"Processed {processed_chunks}/{total_chunks} chunks..."
                    )

                    start_time += chunk_size_s

            self.completed.emit(output_file_path)
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Bird Identification - Desktop (MVP)")
        self.setMinimumWidth(600)

        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setReadOnly(True)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self.on_browse)

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.on_start)

        self.progress = QtWidgets.QProgressBar()
        self.status_label = QtWidgets.QLabel("Idle")

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)

        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(self.file_edit, 1)
        top_row.addWidget(browse_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_row)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log, 1)

        self.worker: AnalysisWorker | None = None

    def on_browse(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select audio file",
            str(Path.home()),
            "Audio Files (*.wav *.mp3 *.flac);;All Files (*)",
        )
        if path:
            self.file_edit.setText(path)
            self.start_btn.setEnabled(True)

    def on_start(self) -> None:
        audio_path = self.file_edit.text().strip()
        if not audio_path:
            return
        self.start_btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("Preparing…")
        self.log.clear()

        self.worker = AnalysisWorker(audio_path)
        self.worker.progress_changed.connect(self.progress.setValue)
        self.worker.status_changed.connect(self.append_log)
        self.worker.completed.connect(self.on_completed)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def append_log(self, text: str) -> None:
        self.status_label.setText(text)
        self.log.appendPlainText(text)

    def on_completed(self, output_path: str) -> None:
        self.append_log(f"Completed. Results: {output_path}")
        self.status_label.setText("Done")
        self.start_btn.setEnabled(True)
        QtWidgets.QMessageBox.information(self, "Done", f"Results saved to:\n{output_path}")

    def on_failed(self, error_message: str) -> None:
        self.append_log(f"Error: {error_message}")
        self.status_label.setText("Failed")
        self.start_btn.setEnabled(True)
        QtWidgets.QMessageBox.critical(self, "Error", error_message)


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


