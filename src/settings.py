"""
settings.py – Einstellungen laden/speichern als JSON
"""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "whisper-mac-app"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS: dict = {
    "hotkey": "ctrl+9",
    "language": "auto",
    "model": "base",
    "sounds_enabled": True,
}


def load_settings() -> dict:
    """Lädt die Einstellungen aus der Konfigurationsdatei."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Fehlende Schlüssel mit Standardwerten auffüllen
            for key, value in DEFAULT_SETTINGS.items():
                data.setdefault(key, value)
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Speichert die Einstellungen in der Konfigurationsdatei."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
