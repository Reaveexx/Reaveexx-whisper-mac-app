"""
recorder.py – Audio-Aufnahme-Logik mit sounddevice
"""

import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import os
from datetime import datetime


class AudioRecorder:
    """Nimmt Audio über das Mikrofon auf und speichert es als WAV-Datei."""

    SAMPLE_RATE = 16000  # Whisper erwartet 16 kHz
    CHANNELS = 1         # Mono

    def __init__(self):
        self._recording = False
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._temp_file: str | None = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Startet die Aufnahme."""
        if self._recording:
            return
        with self._lock:
            self._frames = []
            self._recording = True

        self._stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            dtype="float32",
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> str:
        """Stoppt die Aufnahme und gibt den Pfad zur WAV-Datei zurück."""
        if not self._recording:
            return ""

        self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        return self._save_to_temp_file()

    def _audio_callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        if self._recording:
            with self._lock:
                self._frames.append(indata.copy())

    def _save_to_temp_file(self) -> str:
        """Speichert die aufgenommenen Frames als WAV-Datei."""
        if not self._frames:
            return ""

        audio_data = np.concatenate(self._frames, axis=0)

        # Temporäre Datei erstellen
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="whisper_recording_")
        os.close(fd)

        sf.write(path, audio_data, self.SAMPLE_RATE)
        self._temp_file = path
        return path

    def cleanup(self) -> None:
        """Löscht temporäre Dateien."""
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
            except OSError:
                pass
            self._temp_file = None

    def get_duration(self) -> float:
        """Gibt die aktuelle Aufnahmedauer in Sekunden zurück."""
        with self._lock:
            total_samples = sum(len(f) for f in self._frames)
        return total_samples / self.SAMPLE_RATE
