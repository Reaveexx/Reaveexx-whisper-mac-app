"""
hotkey_manager.py – Globaler Hotkey-Manager mit pynput

Hinweis: Auf macOS sind Accessibility-Berechtigungen erforderlich.
Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen →
Terminal (oder Python) den Zugriff erlauben.
"""

from __future__ import annotations

from typing import Callable

from pynput import keyboard


# Mapping von lesbaren Bezeichnungen auf pynput-Modifier-Keys
_MODIFIER_MAP: dict[str, str] = {
    "ctrl": "<ctrl>",
    "control": "<ctrl>",
    "alt": "<alt>",
    "option": "<alt>",
    "shift": "<shift>",
    "cmd": "<cmd>",
    "command": "<cmd>",
    "super": "<cmd>",
}

# Mapping von lesbaren Bezeichnungen auf Anzeigesymbole
_SYMBOL_MAP: dict[str, str] = {
    "ctrl": "⌃",
    "control": "⌃",
    "alt": "⌥",
    "option": "⌥",
    "shift": "⇧",
    "cmd": "⌘",
    "command": "⌘",
    "super": "⌘",
}


def _format_for_pynput(hotkey_str: str) -> str:
    """Konvertiert 'ctrl+9' → '<ctrl>+9' für pynput GlobalHotKeys."""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    formatted: list[str] = []
    for part in parts:
        formatted.append(_MODIFIER_MAP.get(part, part))
    return "+".join(formatted)


def display_hotkey(hotkey_str: str) -> str:
    """Konvertiert 'ctrl+9' → '⌃9' für die Anzeige im Menü."""
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    result = ""
    for part in parts:
        result += _SYMBOL_MAP.get(part, part.upper())
    return result


class HotkeyManager:
    """
    Registriert und verwaltet einen globalen Hotkey mit pynput.

    Auf macOS müssen Accessibility-Berechtigungen erteilt worden sein,
    damit globale Hotkeys auch in anderen Apps funktionieren.
    """

    def __init__(self, hotkey_str: str, callback: Callable[[], None]) -> None:
        self._hotkey_str = hotkey_str
        self._callback = callback
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> bool:
        """Startet den Hotkey-Listener im Hintergrund. Gibt True bei Erfolg zurück."""
        self.stop()
        pynput_hotkey = _format_for_pynput(self._hotkey_str)
        try:
            self._listener = keyboard.GlobalHotKeys(
                {pynput_hotkey: self._on_hotkey}
            )
            self._listener.start()
            return True
        except Exception:
            # Falls Accessibility-Berechtigung fehlt oder Fehler beim Start
            self._listener = None
            return False

    def stop(self) -> None:
        """Stoppt den Hotkey-Listener."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def update_hotkey(self, hotkey_str: str, callback: Callable[[], None]) -> bool:
        """Aktualisiert Hotkey und Callback und startet den Listener neu. Gibt True bei Erfolg zurück."""
        self._hotkey_str = hotkey_str
        self._callback = callback
        return self.start()

    def _on_hotkey(self) -> None:
        self._callback()
