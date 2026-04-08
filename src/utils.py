"""
utils.py – Hilfsfunktionen
"""

from datetime import datetime


def format_duration(seconds: float) -> str:
    """Formatiert Sekunden als MM:SS."""
    total = int(seconds)
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}:{secs:02d}"


def get_model_info(model_name: str) -> dict:
    """Gibt Infos zu einem Whisper-Modell zurück."""
    info: dict[str, dict[str, str]] = {
        "tiny":   {"size": "~75 MB",  "speed": "Sehr schnell", "quality": "Niedrig"},
        "base":   {"size": "~145 MB", "speed": "Schnell",       "quality": "Gut"},
        "small":  {"size": "~465 MB", "speed": "Mittel",        "quality": "Besser"},
        "medium": {"size": "~1,5 GB", "speed": "Langsam",       "quality": "Sehr gut"},
        "large":  {"size": "~2,9 GB", "speed": "Sehr langsam",  "quality": "Exzellent"},
    }
    return info.get(model_name, {})
