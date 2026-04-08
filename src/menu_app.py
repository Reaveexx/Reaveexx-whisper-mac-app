"""
menu_app.py – macOS Menüleisten-App mit rumps

Das Mikrofon-Icon sitzt in der macOS-Menüleiste. Per globalem Hotkey
(Standard: Ctrl+9) wird die Aufnahme gestartet/gestoppt. Nach der
Transkription mit Whisper wird der Text automatisch in die Zwischenablage
kopiert.
"""

from __future__ import annotations

import subprocess
import threading

import rumps

from .recorder import AudioRecorder
from .transcriber import Transcriber, LANGUAGE_MAP, AVAILABLE_MODELS
from .hotkey_manager import HotkeyManager, display_hotkey
from .settings import load_settings, save_settings
from .sounds import play_sound

# Menüleisten-Titel
_TITLE_IDLE = "🎙️"
_TITLE_RECORDING = "🔴"
_TITLE_PROCESSING = "⏳"


class WhisperMenuApp(rumps.App):
    """Hauptklasse der Menüleisten-App."""

    def __init__(self) -> None:
        self._settings = load_settings()

        super().__init__(
            name="Whisper Mac App",
            title=_TITLE_IDLE,
            quit_button=None,
        )

        self._recorder = AudioRecorder()
        self._transcriber = Transcriber(self._settings["model"])
        self._is_recording = False
        self._is_transcribing = False

        self._build_menu()

        # Globalen Hotkey-Listener starten
        self._hotkey_manager = HotkeyManager(
            self._settings["hotkey"],
            self._toggle_recording,
        )
        hotkey_ok = self._hotkey_manager.start()
        if not hotkey_ok:
            rumps.notification(
                title="Whisper Mac App",
                subtitle="⚠️ Hotkey nicht aktiv",
                message=(
                    "Accessibility-Berechtigung fehlt. "
                    "Systemeinstellungen → Datenschutz & Sicherheit → "
                    "Bedienungshilfen → Terminal erlauben, dann App neu starten."
                ),
                sound=False,
            )

    # ------------------------------------------------------------------ #
    # Menü aufbauen                                                        #
    # ------------------------------------------------------------------ #

    def _build_menu(self) -> None:
        # Status-Anzeige (nicht klickbar)
        self._status_item = rumps.MenuItem("● Bereit")
        self._status_item.set_callback(None)

        # Hotkey-Anzeige (nicht klickbar)
        display = display_hotkey(self._settings["hotkey"])
        self._hotkey_display = rumps.MenuItem(f"Hotkey: {display}")
        self._hotkey_display.set_callback(None)

        # Sprache-Untermenü
        language_menu = rumps.MenuItem("🌍 Sprache")
        current_lang = self._settings.get("language", "auto")
        # Map language menu item title → lang_code for checkmark updates
        self._lang_code_map: dict[str, str] = {}
        for name, code in LANGUAGE_MAP.items():
            lang_code = code if code else "auto"
            self._lang_code_map[name] = lang_code
            item = rumps.MenuItem(
                name,
                callback=lambda sender, lc=lang_code: self._on_language_change(lc),
            )
            if lang_code == current_lang:
                item.title = f"✓ {name}"
            language_menu.add(item)

        # Modell-Untermenü
        model_menu = rumps.MenuItem("🤖 Whisper-Modell")
        current_model = self._settings.get("model", "base")
        for model in AVAILABLE_MODELS:
            item = rumps.MenuItem(model, callback=self._on_model_change)
            if model == current_model:
                item.title = f"✓ {model}"
            model_menu.add(item)

        # Hotkey konfigurieren
        hotkey_config = rumps.MenuItem(
            "⌨️  Hotkey konfigurieren…", callback=self._on_configure_hotkey
        )

        # Sounds umschalten
        sounds_label = (
            "🔊 Sounds: An" if self._settings["sounds_enabled"] else "🔇 Sounds: Aus"
        )
        self._sounds_toggle = rumps.MenuItem(sounds_label, callback=self._on_toggle_sounds)

        # Beenden
        quit_item = rumps.MenuItem("Beenden", callback=self._on_quit)

        self.menu = [
            self._status_item,
            self._hotkey_display,
            rumps.separator,
            language_menu,
            model_menu,
            rumps.separator,
            hotkey_config,
            self._sounds_toggle,
            rumps.separator,
            quit_item,
        ]

    # ------------------------------------------------------------------ #
    # Aufnahme-Steuerung                                                   #
    # ------------------------------------------------------------------ #

    def _toggle_recording(self) -> None:
        """Wird vom globalen Hotkey aufgerufen (Background-Thread)."""
        if self._is_transcribing:
            return
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        self._is_recording = True
        self.title = _TITLE_RECORDING
        self._status_item.title = "● Aufnahme läuft…"

        if self._settings["sounds_enabled"]:
            play_sound("start")

        rumps.notification(
            title="Whisper Mac App",
            subtitle="🎤 Aufnahme gestartet",
            message=f"Drücke {display_hotkey(self._settings['hotkey'])} erneut zum Stoppen.",
            sound=False,
        )

        self._recorder.start()

    def _stop_recording(self) -> None:
        self._is_recording = False
        self.title = _TITLE_PROCESSING
        self._status_item.title = "● Transkribiert…"

        if self._settings["sounds_enabled"]:
            play_sound("stop")

        audio_path = self._recorder.stop()

        if not audio_path:
            self._reset_status()
            rumps.notification(
                title="Whisper Mac App",
                subtitle="⚠️ Keine Aufnahme",
                message="Die Aufnahme war zu kurz oder leer.",
                sound=False,
            )
            return

        # Transkription im Hintergrund starten
        self._is_transcribing = True
        threading.Thread(
            target=self._run_transcription,
            args=(audio_path,),
            daemon=True,
        ).start()

    # ------------------------------------------------------------------ #
    # Transkription                                                         #
    # ------------------------------------------------------------------ #

    def _run_transcription(self, audio_path: str) -> None:
        """Läuft in einem Background-Thread."""
        try:
            lang_code = self._settings.get("language", "auto")
            if lang_code == "auto":
                lang_code = None

            text = self._transcriber.transcribe(audio_path, language=lang_code)

            if text:
                self._copy_to_clipboard(text)

                if self._settings["sounds_enabled"]:
                    play_sound("success")

                rumps.notification(
                    title="Whisper Mac App",
                    subtitle="✅ Transkription fertig",
                    message="Text in Zwischenablage kopiert!",
                    sound=False,
                )
            else:
                rumps.notification(
                    title="Whisper Mac App",
                    subtitle="⚠️ Kein Text erkannt",
                    message="Bitte erneut versuchen.",
                    sound=False,
                )
        except Exception:
            rumps.notification(
                title="Whisper Mac App",
                subtitle="❌ Transkription fehlgeschlagen",
                message="Bitte prüfe das Mikrofon und versuche es erneut.",
                sound=False,
            )
        finally:
            self._is_transcribing = False
            self._recorder.cleanup()
            self._reset_status()

    def _reset_status(self) -> None:
        self.title = _TITLE_IDLE
        self._status_item.title = "● Bereit"

    # ------------------------------------------------------------------ #
    # Hilfsmethoden                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _copy_to_clipboard(text: str) -> None:
        """Kopiert Text in die macOS-Zwischenablage via pbcopy."""
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        process.communicate(text.encode("utf-8"))

    # ------------------------------------------------------------------ #
    # Menü-Callbacks                                                       #
    # ------------------------------------------------------------------ #

    def _on_language_change(self, lang_code: str) -> None:
        self._settings["language"] = lang_code
        save_settings(self._settings)

        # Häkchen aktualisieren
        language_menu = self.menu.get("🌍 Sprache")
        if language_menu:
            for item in language_menu.values():
                base_title = item.title.lstrip("✓").strip()
                item_code = self._lang_code_map.get(base_title, "auto")
                item.title = f"✓ {base_title}" if item_code == lang_code else base_title

    def _on_model_change(self, sender: rumps.MenuItem) -> None:
        model_name = sender.title.lstrip("✓ ").strip()
        self._settings["model"] = model_name
        save_settings(self._settings)

        # Häkchen aktualisieren
        model_menu = self.menu.get("🤖 Whisper-Modell")
        if model_menu:
            for item in model_menu.values():
                base = item.title.lstrip("✓ ").strip()
                item.title = f"✓ {base}" if base == model_name else base

        # Modell neu laden beim nächsten Verwenden
        self._transcriber.unload_model()
        self._transcriber = Transcriber(model_name)

    def _on_configure_hotkey(self, _: rumps.MenuItem) -> None:
        window = rumps.Window(
            message="Gib den neuen Hotkey ein.\nFormat: ctrl+9 | ctrl+shift+r | cmd+alt+s",
            title="⌨️  Hotkey konfigurieren",
            default_text=self._settings["hotkey"],
            ok="Speichern",
            cancel="Abbrechen",
            dimensions=(320, 22),
        )
        response = window.run()

        if response.clicked and response.text.strip():
            new_hotkey = response.text.strip().lower()
            self._settings["hotkey"] = new_hotkey
            save_settings(self._settings)

            # Anzeige im Menü aktualisieren
            display = display_hotkey(new_hotkey)
            self._hotkey_display.title = f"Hotkey: {display}"

            # Listener mit neuem Hotkey neu starten
            ok = self._hotkey_manager.update_hotkey(new_hotkey, self._toggle_recording)
            if not ok:
                rumps.notification(
                    title="Whisper Mac App",
                    subtitle="⚠️ Hotkey nicht aktiv",
                    message=(
                        "Accessibility-Berechtigung fehlt. "
                        "Bitte erteile die Berechtigung und starte die App neu."
                    ),
                    sound=False,
                )

    def _on_toggle_sounds(self, sender: rumps.MenuItem) -> None:
        self._settings["sounds_enabled"] = not self._settings["sounds_enabled"]
        sender.title = (
            "🔊 Sounds: An" if self._settings["sounds_enabled"] else "🔇 Sounds: Aus"
        )
        save_settings(self._settings)

    def _on_quit(self, _: rumps.MenuItem) -> None:
        self._hotkey_manager.stop()
        self._recorder.cleanup()
        rumps.quit_application()
