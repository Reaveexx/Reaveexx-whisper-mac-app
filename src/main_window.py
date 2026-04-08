"""
main_window.py – Haupt-GUI-Fenster (PyQt6, natives macOS Design)
"""

import os
import threading
import time

from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSignal,
    QObject,
    QThread,
)
from PyQt6.QtGui import QColor, QFont, QPalette, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.recorder import AudioRecorder
from src.transcriber import Transcriber, AVAILABLE_MODELS, LANGUAGE_MAP
from src.utils import format_duration, save_text_to_file, get_model_info


# ---------------------------------------------------------------------------
# Worker-Thread für die Transkription (damit die GUI nicht einfriert)
# ---------------------------------------------------------------------------

class TranscribeWorker(QObject):
    """Führt die Whisper-Transkription in einem Hintergrund-Thread aus."""

    finished = pyqtSignal(str)       # Transkriptionsergebnis
    error = pyqtSignal(str)          # Fehlermeldung
    status = pyqtSignal(str)         # Statusmeldung

    def __init__(
        self,
        transcriber: Transcriber,
        audio_path: str,
        language: str | None,
        model_name: str,
    ):
        super().__init__()
        self._transcriber = transcriber
        self._audio_path = audio_path
        self._language = language
        self._model_name = model_name

    def run(self) -> None:
        try:
            # Modell neu laden falls geändert
            if (
                not self._transcriber.is_loaded
                or self._transcriber.model_name != self._model_name
            ):
                self._transcriber.load_model(
                    self._model_name,
                    progress_callback=lambda msg: self.status.emit(msg),
                )

            text = self._transcriber.transcribe(
                self._audio_path,
                language=self._language,
                progress_callback=lambda msg: self.status.emit(msg),
            )
            self.finished.emit(text)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


# ---------------------------------------------------------------------------
# Haupt-Fenster
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Haupt-GUI-Fenster der Whisper Mac App."""

    # Internes Signal, damit der Hintergrund-Thread die GUI aktualisieren kann
    _status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._recorder = AudioRecorder()
        self._transcriber = Transcriber(model_name="base")
        self._audio_path: str = ""
        self._duration_timer = QTimer(self)
        self._duration_timer.setInterval(500)
        self._duration_timer.timeout.connect(self._update_duration)
        self._worker_thread: QThread | None = None

        self._build_ui()
        self._connect_signals()
        self._apply_stylesheet()
        self.setAcceptDrops(True)

    # ------------------------------------------------------------------
    # UI-Aufbau
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setWindowTitle("Whisper Mac App")
        self.setMinimumSize(700, 580)
        self.resize(800, 650)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # ---- Titel ----
        title = QLabel("🎙️ Whisper Mac App")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel("Lokale Sprach-zu-Text Transkription – komplett offline")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        # ---- Einstellungszeile ----
        settings_row = QHBoxLayout()
        settings_row.setSpacing(12)

        # Sprachauswahl
        lang_label = QLabel("Sprache:")
        lang_label.setObjectName("settingsLabel")
        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("settingsCombo")
        self._lang_combo.addItems(list(LANGUAGE_MAP.keys()))
        self._lang_combo.setCurrentText("Auto-Detect")
        self._lang_combo.setMinimumWidth(150)

        # Modellauswahl
        model_label = QLabel("Modell:")
        model_label.setObjectName("settingsLabel")
        self._model_combo = QComboBox()
        self._model_combo.setObjectName("settingsCombo")
        self._model_combo.addItems(AVAILABLE_MODELS)
        self._model_combo.setCurrentText("base")
        self._model_combo.setMinimumWidth(110)
        self._model_combo.currentTextChanged.connect(self._on_model_changed)

        # Modell-Info-Label
        self._model_info_label = QLabel()
        self._model_info_label.setObjectName("modelInfo")
        self._update_model_info("base")

        settings_row.addWidget(lang_label)
        settings_row.addWidget(self._lang_combo)
        settings_row.addSpacing(8)
        settings_row.addWidget(model_label)
        settings_row.addWidget(self._model_combo)
        settings_row.addSpacing(8)
        settings_row.addWidget(self._model_info_label)
        settings_row.addStretch()
        root.addLayout(settings_row)

        # ---- Trennlinie ----
        root.addWidget(self._make_separator())

        # ---- Aufnahme-Button + Dauer ----
        record_row = QHBoxLayout()
        record_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        record_row.setSpacing(20)

        self._record_btn = QPushButton("⏺  Aufnahme starten")
        self._record_btn.setObjectName("recordButton")
        self._record_btn.setFixedSize(220, 52)
        self._record_btn.clicked.connect(self._toggle_recording)

        self._duration_label = QLabel("00:00")
        self._duration_label.setObjectName("durationLabel")
        self._duration_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        record_row.addWidget(self._record_btn)
        record_row.addWidget(self._duration_label)
        root.addLayout(record_row)

        # ---- Status-Label ----
        self._status_label = QLabel("Bereit")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._status_label)

        # ---- Fortschrittsbalken ----
        self._progress = QProgressBar()
        self._progress.setObjectName("progressBar")
        self._progress.setRange(0, 0)  # Unbestimmter Fortschritt
        self._progress.setVisible(False)
        self._progress.setFixedHeight(6)
        root.addWidget(self._progress)

        # ---- Transkriptions-Textfeld ----
        text_label = QLabel("Transkription:")
        text_label.setObjectName("sectionLabel")
        root.addWidget(text_label)

        self._text_edit = QTextEdit()
        self._text_edit.setObjectName("transcriptionText")
        self._text_edit.setPlaceholderText(
            "Das transkribierte Ergebnis erscheint hier…\n\n"
            "Tipp: Du kannst auch eine Audio-Datei hierher ziehen (Drag & Drop)."
        )
        self._text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root.addWidget(self._text_edit)

        # ---- Aktions-Buttons ----
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._copy_btn = QPushButton("📋  Kopieren")
        self._copy_btn.setObjectName("actionButton")
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        self._copy_btn.setEnabled(False)

        self._save_btn = QPushButton("💾  Als Textdatei speichern")
        self._save_btn.setObjectName("actionButton")
        self._save_btn.clicked.connect(self._save_to_file)
        self._save_btn.setEnabled(False)

        self._clear_btn = QPushButton("🗑  Löschen")
        self._clear_btn.setObjectName("actionButton")
        self._clear_btn.clicked.connect(self._clear_text)
        self._clear_btn.setEnabled(False)

        action_row.addWidget(self._copy_btn)
        action_row.addWidget(self._save_btn)
        action_row.addStretch()
        action_row.addWidget(self._clear_btn)
        root.addLayout(action_row)

        # ---- Statusleiste ----
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(
            "Bereit · Ziehe eine Audio-Datei ins Fenster, um sie zu transkribieren"
        )

    def _connect_signals(self) -> None:
        self._status_update.connect(self._on_status_update)

    def _make_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setObjectName("separator")
        return line

    # ------------------------------------------------------------------
    # Stylesheet / Design
    # ------------------------------------------------------------------

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: -apple-system, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
            }

            #title {
                font-size: 26px;
                font-weight: 700;
                color: #cba6f7;
                margin-bottom: 2px;
            }

            #subtitle {
                font-size: 13px;
                color: #a6adc8;
                margin-bottom: 4px;
            }

            #settingsLabel {
                color: #a6adc8;
                font-size: 13px;
            }

            #settingsCombo {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 13px;
            }

            #settingsCombo::drop-down {
                border: none;
                width: 20px;
            }

            #settingsCombo QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #cba6f7;
                selection-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 6px;
            }

            #modelInfo {
                color: #6c7086;
                font-size: 12px;
            }

            #separator {
                color: #313244;
                margin: 4px 0;
            }

            #recordButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                font-size: 16px;
                font-weight: 700;
                border: none;
                border-radius: 14px;
                padding: 0 20px;
            }

            #recordButton:hover {
                background-color: #eba0ac;
            }

            #recordButton:pressed {
                background-color: #e07a91;
            }

            #recordButton[recording="true"] {
                background-color: #a6e3a1;
                color: #1e1e2e;
            }

            #recordButton[recording="true"]:hover {
                background-color: #94d88e;
            }

            #durationLabel {
                font-size: 22px;
                font-weight: 600;
                color: #cba6f7;
                min-width: 70px;
            }

            #statusLabel {
                font-size: 13px;
                color: #89b4fa;
            }

            #progressBar {
                background-color: #313244;
                border: none;
                border-radius: 3px;
            }

            #progressBar::chunk {
                background-color: #cba6f7;
                border-radius: 3px;
            }

            #sectionLabel {
                font-size: 13px;
                color: #a6adc8;
                font-weight: 600;
            }

            #transcriptionText {
                background-color: #181825;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.5;
                selection-background-color: #cba6f7;
                selection-color: #1e1e2e;
            }

            #transcriptionText QScrollBar:vertical {
                background-color: #1e1e2e;
                width: 8px;
                border-radius: 4px;
            }

            #transcriptionText QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 4px;
            }

            #actionButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 10px;
                padding: 8px 18px;
                font-size: 13px;
            }

            #actionButton:hover {
                background-color: #45475a;
            }

            #actionButton:pressed {
                background-color: #585b70;
            }

            #actionButton:disabled {
                color: #585b70;
                border-color: #313244;
            }

            QStatusBar {
                background-color: #181825;
                color: #6c7086;
                font-size: 12px;
                border-top: 1px solid #313244;
            }

            QMessageBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
        """)

    # ------------------------------------------------------------------
    # Slots / Event-Handler
    # ------------------------------------------------------------------

    def _toggle_recording(self) -> None:
        if self._recorder.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        try:
            self._recorder.start()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Mikrofon-Fehler",
                f"Mikrofon konnte nicht geöffnet werden:\n{exc}",
            )
            return

        self._record_btn.setText("⏹  Aufnahme stoppen")
        self._record_btn.setProperty("recording", "true")
        self._record_btn.style().unpolish(self._record_btn)
        self._record_btn.style().polish(self._record_btn)
        self._status_label.setText("🔴 Aufnahme läuft…")
        self._duration_label.setText("00:00")
        self._duration_timer.start()
        self._set_action_buttons_enabled(False)

    def _stop_recording(self) -> None:
        self._duration_timer.stop()
        audio_path = self._recorder.stop()
        self._record_btn.setText("⏺  Aufnahme starten")
        self._record_btn.setProperty("recording", "false")
        self._record_btn.style().unpolish(self._record_btn)
        self._record_btn.style().polish(self._record_btn)
        self._record_btn.setEnabled(False)

        if not audio_path:
            self._status_label.setText("Keine Audiodaten – bitte erneut versuchen.")
            self._record_btn.setEnabled(True)
            return

        self._audio_path = audio_path
        self._start_transcription(audio_path)

    def _start_transcription(self, audio_path: str) -> None:
        lang_name = self._lang_combo.currentText()
        language = LANGUAGE_MAP.get(lang_name)
        model_name = self._model_combo.currentText()

        self._status_label.setText("⏳ Transkribiere…")
        self._progress.setVisible(True)

        self._worker = TranscribeWorker(
            self._transcriber, audio_path, language, model_name
        )
        self._worker_thread = QThread()
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_transcription_done)
        self._worker.error.connect(self._on_transcription_error)
        self._worker.status.connect(self._on_status_update)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.error.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()

    def _on_transcription_done(self, text: str) -> None:
        self._progress.setVisible(False)
        self._text_edit.setPlainText(text)
        self._status_label.setText("✅ Transkription abgeschlossen")
        self._record_btn.setEnabled(True)
        self._set_action_buttons_enabled(True)
        self._recorder.cleanup()
        self.statusBar().showMessage(f"Fertig · {len(text)} Zeichen transkribiert")

    def _on_transcription_error(self, error_msg: str) -> None:
        self._progress.setVisible(False)
        self._status_label.setText("❌ Fehler bei der Transkription")
        self._record_btn.setEnabled(True)
        QMessageBox.critical(
            self,
            "Transkriptions-Fehler",
            f"Fehler:\n{error_msg}",
        )

    def _on_status_update(self, msg: str) -> None:
        self._status_label.setText(f"⏳ {msg}")

    def _update_duration(self) -> None:
        duration = self._recorder.get_duration()
        self._duration_label.setText(format_duration(duration))

    def _on_model_changed(self, model_name: str) -> None:
        self._update_model_info(model_name)
        # Modell muss beim nächsten Transkribieren neu geladen werden
        self._transcriber.unload_model()

    def _update_model_info(self, model_name: str) -> None:
        info = get_model_info(model_name)
        if info:
            self._model_info_label.setText(
                f"{info['size']} · {info['speed']} · {info['quality']}"
            )

    def _copy_to_clipboard(self) -> None:
        text = self._text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("Text in Zwischenablage kopiert ✓")

    def _save_to_file(self) -> None:
        text = self._text_edit.toPlainText()
        if not text:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Transkription speichern",
            os.path.join(os.path.expanduser("~"), "Desktop", "transkription.txt"),
            "Textdateien (*.txt);;Alle Dateien (*)",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                self.statusBar().showMessage(f"Gespeichert: {path}")
            except OSError as exc:
                QMessageBox.critical(self, "Fehler", f"Datei konnte nicht gespeichert werden:\n{exc}")

    def _clear_text(self) -> None:
        self._text_edit.clear()
        self._set_action_buttons_enabled(False)
        self._status_label.setText("Bereit")
        self._duration_label.setText("00:00")
        self.statusBar().showMessage("Text gelöscht")

    def _set_action_buttons_enabled(self, enabled: bool) -> None:
        self._copy_btn.setEnabled(enabled)
        self._save_btn.setEnabled(enabled)
        self._clear_btn.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Drag & Drop für Audio-Dateien
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(
                    (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aiff", ".aac")
                ):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(
                (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aiff", ".aac")
            ):
                self._audio_path = path
                self._status_label.setText(f"Datei geladen: {os.path.basename(path)}")
                self.statusBar().showMessage(f"Audio-Datei: {path}")
                self._start_transcription(path)
                break

    def closeEvent(self, event) -> None:
        if self._recorder.is_recording:
            self._recorder.stop()
        self._recorder.cleanup()
        event.accept()
