"""
utils.py – Hilfsfunktionen
"""

import os
from datetime import datetime


def format_duration(seconds: float) -> str:
    """Formatiert Sekunden als MM:SS."""
    total = int(seconds)
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}:{secs:02d}"


def save_text_to_file(text: str, directory: str | None = None) -> str:
    """
    Speichert Text in einer .txt-Datei.

    Returns
    -------
    str
        Pfad zur gespeicherten Datei.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transkription_{timestamp}.txt"
    if directory:
        path = os.path.join(directory, filename)
    else:
        path = os.path.join(os.path.expanduser("~"), "Desktop", filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return path


def get_model_info(model_name: str) -> dict:
    """Gibt Infos zu einem Whisper-Modell zurück."""
    info = {
        "tiny":   {"size": "~75 MB",  "speed": "Sehr schnell", "quality": "Niedrig"},
        "base":   {"size": "~145 MB", "speed": "Schnell",       "quality": "Gut"},
        "small":  {"size": "~465 MB", "speed": "Mittel",        "quality": "Besser"},
        "medium": {"size": "~1,5 GB", "speed": "Langsam",       "quality": "Sehr gut"},
        "large":  {"size": "~2,9 GB", "speed": "Sehr langsam",  "quality": "Exzellent"},
    }
    return info.get(model_name, {})
