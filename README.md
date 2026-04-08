# 🎙️ Whisper Mac App – Menüleisten-App

Eine macOS **Menüleisten-App** für lokale Sprach-zu-Text-Transkription mit OpenAI Whisper. Die App sitzt unsichtbar als kleines Mikrofon-Icon in der Menüleiste und reagiert auf einen **konfigurierbaren globalen Hotkey** – völlig offline, ohne Cloud und ohne API-Key.

---

## 🚀 Wie es funktioniert

1. Die App startet → kleines 🎙️-Icon erscheint in der macOS-Menüleiste
2. **`Ctrl+9` drücken** → 🔊 Ping-Sound + Notification „🎤 Aufnahme gestartet"
3. **Sprechen** (beliebig lang)
4. **`Ctrl+9` nochmal drücken** → 🔊 Pop-Sound → Whisper transkribiert lokal
5. **Fertig** → 🔊 Glass-Sound + Notification „✅ Text in Zwischenablage kopiert!"
6. **`Cmd+V`** drücken → Text einfügen

> Der Hotkey ist frei konfigurierbar über das Menü → „⌨️  Hotkey konfigurieren…"

---

## 📋 Funktionen

| Feature | Details |
|---------|---------|
| 🎤 Globaler Hotkey | Aufnahme starten/stoppen aus jeder App heraus |
| 📋 Auto-Zwischenablage | Text wird automatisch nach der Transkription kopiert |
| 🌍 Mehrsprachigkeit | Auto-Detect + 12 Sprachen |
| 🤖 Modell-Auswahl | tiny, base, small, medium, large |
| 🔊 Sound-Feedback | Systemsounds bei Start, Stop und Erfolg |
| 💾 Persistente Einstellungen | Hotkey, Sprache, Modell werden gespeichert |
| 👻 Kein Dock-Icon | App läuft unsichtbar im Hintergrund |
| 🔒 Komplett offline | Keine Cloud, kein Internet, kein API-Key |

---

## 🛠️ Installation

### Voraussetzungen

- **macOS** 12 oder neuer
- **Python 3.10+** (empfohlen via [Homebrew](https://brew.sh)):
  ```bash
  brew install python
  ```
- **FFmpeg** (für Whisper):
  ```bash
  brew install ffmpeg
  ```

### App installieren

```bash
# 1. Repository klonen
git clone https://github.com/Reaveexx/Reaveexx-whisper-mac-app.git
cd Reaveexx-whisper-mac-app

# 2. Virtuelle Umgebung erstellen (empfohlen)
python3 -m venv .venv
source .venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt
```

> **Hinweis:** Die Installation kann einige Minuten dauern, da PyTorch und Whisper heruntergeladen werden.

---

## 🚀 App starten

```bash
# Virtuelle Umgebung aktivieren (falls noch nicht aktiv)
source .venv/bin/activate

# App starten
python app.py
```

Nach dem Start erscheint das 🎙️-Icon in deiner macOS-Menüleiste.

---

## ⌨️ Hotkey konfigurieren

1. Klicke auf das 🎙️-Icon in der Menüleiste
2. Wähle **„⌨️  Hotkey konfigurieren…"**
3. Gib deine gewünschte Tastenkombination ein (z.B. `ctrl+9`, `ctrl+shift+r`, `cmd+alt+s`)
4. Klicke **„Speichern"**

Der neue Hotkey ist sofort aktiv und wird dauerhaft gespeichert.

### Format für Hotkeys

| Taste | Eingabe |
|-------|---------|
| Control | `ctrl` |
| Alt / Option | `alt` |
| Shift | `shift` |
| Command | `cmd` |
| Buchstabe/Zahl | `a`, `9`, `r` |

**Beispiele:** `ctrl+9` · `ctrl+shift+r` · `cmd+alt+s`

---

### ⚠️ Accessibility-Berechtigung (wichtig!)

Damit der globale Hotkey **auch funktioniert, wenn eine andere App aktiv ist**, muss macOS dem Terminal (oder Python) die Accessibility-Berechtigung erteilen:

1. **Systemeinstellungen** öffnen
2. **Datenschutz & Sicherheit** → **Bedienungshilfen**
3. **Terminal** (oder deine Python-App) zur Liste hinzufügen und aktivieren
4. **App neu starten** – die Berechtigung wird erst nach einem Neustart der App wirksam

> Ohne diese Berechtigung funktioniert der Hotkey nur, wenn die Menüleiste aktiv ist.
> Die App zeigt beim Start eine Hinweis-Notification, wenn die Berechtigung fehlt.

---

## 🤖 Whisper-Modelle

| Modell | Größe | Geschwindigkeit | Qualität | Empfehlung |
|--------|-------|-----------------|----------|------------|
| `tiny` | ~75 MB | Sehr schnell | Niedrig | Schnelle Tests |
| `base` | ~145 MB | Schnell | Gut | **Standard (empfohlen)** |
| `small` | ~465 MB | Mittel | Besser | Bessere Genauigkeit |
| `medium` | ~1,5 GB | Langsam | Sehr gut | Hochwertige Transkription |
| `large` | ~2,9 GB | Sehr langsam | Exzellent | Beste Qualität |

> Modelle werden beim ersten Verwenden automatisch in `~/.cache/whisper/` heruntergeladen.

Das Modell kann jederzeit über das Menü → **„🤖 Whisper-Modell"** gewechselt werden.

---

## 🌍 Unterstützte Sprachen

Auto-Detect, Deutsch, Englisch, Französisch, Spanisch, Italienisch, Portugiesisch, Niederländisch, Polnisch, Russisch, Chinesisch, Japanisch, Koreanisch

---

## 📁 Projektstruktur

```
Reaveexx-whisper-mac-app/
├── README.md                # Diese Datei
├── requirements.txt         # Python-Abhängigkeiten
├── app.py                   # Einstiegspunkt – App starten
└── src/
    ├── __init__.py
    ├── menu_app.py          # Menüleisten-App (rumps)
    ├── recorder.py          # Mikrofon-Aufnahme (sounddevice)
    ├── transcriber.py       # Whisper-Transkription
    ├── hotkey_manager.py    # Globaler Hotkey (pynput)
    ├── settings.py          # Einstellungen laden/speichern (JSON)
    ├── sounds.py            # Sound-Feedback (afplay)
    └── utils.py             # Hilfsfunktionen
```

Einstellungen werden gespeichert unter: `~/.config/whisper-mac-app/settings.json`

---

## 🐛 Fehlerbehebung

### Hotkey funktioniert nicht in anderen Apps
→ Accessibility-Berechtigung erteilen (siehe oben)

### „Mikrofon-Fehler" beim Start
→ **Systemeinstellungen → Datenschutz & Sicherheit → Mikrofon** → Terminal erlauben

### FFmpeg nicht gefunden
```bash
brew install ffmpeg
```

### App erscheint nicht in der Menüleiste
```bash
# Prüfe ob die App läuft
python app.py
```

### Zu viele Icons in der Menüleiste
→ Halte `Cmd` gedrückt und ziehe das Icon aus der Menüleiste heraus, um es zu entfernen (dann App neu starten)

---

## 📄 Lizenz

MIT License – frei verwendbar und veränderbar.

