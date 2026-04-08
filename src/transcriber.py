"""
transcriber.py – Whisper-Transkriptions-Logik
"""

from typing import Callable
import whisper
import numpy as np


AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

LANGUAGE_MAP = {
    "Auto-Detect": None,
    "Deutsch": "de",
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Portugiesisch": "pt",
    "Niederländisch": "nl",
    "Polnisch": "pl",
    "Russisch": "ru",
    "Chinesisch": "zh",
    "Japanisch": "ja",
    "Koreanisch": "ko",
}


class Transcriber:
    """Lädt ein Whisper-Modell und transkribiert Audio-Dateien."""

    def __init__(self, model_name: str = "base"):
        self._model_name = model_name
        self._model = None

    def load_model(
        self,
        model_name: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        """Lädt das Whisper-Modell (kann einige Zeit dauern)."""
        name = model_name or self._model_name
        if progress_callback:
            progress_callback(f"Lade Whisper-Modell '{name}'…")
        self._model = whisper.load_model(name)
        self._model_name = name

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """
        Transkribiert eine Audio-Datei.

        Parameters
        ----------
        audio_path : str
            Pfad zur WAV-Datei.
        language : str | None
            ISO 639-1 Sprachcode (z. B. 'de') oder None für Auto-Detect.
        progress_callback : callable, optional
            Wird mit Status-Strings aufgerufen.

        Returns
        -------
        str
            Der transkribierte Text.
        """
        if self._model is None:
            self.load_model(progress_callback=progress_callback)

        if progress_callback:
            progress_callback("Transkribiere Audio…")

        options: dict = {"fp16": False}
        if language:
            options["language"] = language

        result = self._model.transcribe(audio_path, **options)
        return result["text"].strip()

    def unload_model(self) -> None:
        """Entlädt das aktuelle Modell, damit beim nächsten Aufruf neu geladen wird."""
        self._model = None

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
