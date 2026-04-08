#!/usr/bin/env python3
"""
Whisper Mac App – Einstiegspunkt
Startet die macOS Menüleisten-App.
"""

import sys
import os

# Sicherstellen, dass das src-Verzeichnis im Pfad ist
sys.path.insert(0, os.path.dirname(__file__))

from src.menu_app import WhisperMenuApp


def main() -> None:
    app = WhisperMenuApp()
    app.run()


if __name__ == "__main__":
    main()
