#!/usr/bin/env python3
"""
Whisper Mac App – Einstiegspunkt
Startet die native macOS Speech-to-Text Anwendung.
"""

import sys
import os

# Sicherstellen, dass das src-Verzeichnis im Pfad ist
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Whisper Mac App")
    app.setOrganizationName("Reaveexx")
    app.setApplicationDisplayName("Whisper Mac App")

    # Natives macOS Look & Feel
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
