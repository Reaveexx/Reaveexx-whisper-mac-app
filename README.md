# 🎙️ Whisper Mac App

Eine native macOS Desktop-App für lokale Sprach-zu-Text-Transkription mit OpenAI Whisper – komplett offline, ohne Browser und ohne Internetverbindung.

---

## 📋 Beschreibung

Die **Whisper Mac App** nimmt Sprache über dein Mikrofon auf und wandelt sie mithilfe des lokal ausgeführten [OpenAI Whisper](https://github.com/openai/whisper)-Modells in Text um. Die Transkription findet vollständig auf deinem Mac statt – kein Internet, kein API-Key, keine Cloud.

### Funktionen

| Feature | Details |
|---|---|
| 🎤 Mikrofon-Aufnahme | Start/Stop per Knopfdruck, Aufnahme-Dauer-Anzeige |
| 📝 Lokale Transkription | Whisper läuft direkt auf deinem Mac (keine Cloud) |
| 🌍 Mehrsprachigkeit | Deutsch, Englisch, Französisch, Spanisch, Italienisch u.v.m. + Auto-Detect |
| 🖥️ Native macOS GUI | Schönes Dark-Mode Design mit PyQt6 |
| 📋 Zwischenablage | Ergebnis mit einem Klick kopieren |
| 💾 Export | Transkription als `.txt`-Datei speichern |
| 🗂️ Drag & Drop | Audio-Dateien direkt ins Fenster ziehen |
| 🔧 Modell-Auswahl | tiny, base, small, medium, large |

---

## 🛠️ Installation

### Voraussetzungen

- **macOS** 12 oder neuer
- **Python 3.10+** – [python.org](https://www.python.org/downloads/)
- **Homebrew** (empfohlen) – [brew.sh](https://brew.sh)
- **FFmpeg** (für Whisper erforderlich):

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

> **Hinweis:** Das Installieren aller Pakete kann einige Minuten dauern, da PyTorch und Whisper heruntergeladen werden.

---

## 🚀 App starten

```bash
# Virtuelle Umgebung aktivieren (falls noch nicht aktiv)
source .venv/bin/activate

# App starten
python app.py
```

Beim ersten Start eines neuen Whisper-Modells wird dieses automatisch heruntergeladen und lokal gecacht. Ab dann funktioniert alles ohne Internet.

---

## 🎛️ Bedienung

1. **Sprache wählen** – Wähle die Sprache aus dem Dropdown oder nutze „Auto-Detect"
2. **Whisper-Modell wählen** – Kleiner = schneller, Größer = genauer (Standard: `base`)
3. **Aufnahme starten** – Klick auf den roten Button
4. **Sprechen** – Die Dauer-Anzeige zeigt wie lange du aufnimmst
5. **Aufnahme stoppen** – Klick erneut auf den Button
6. **Ergebnis** – Der transkribierte Text erscheint automatisch
7. **Exportieren** – Kopieren oder als `.txt` speichern

**Drag & Drop:** Ziehe direkt eine Audio-Datei (`.wav`, `.mp3`, `.m4a`, `.flac` etc.) ins Fenster, um sie zu transkribieren.

---

## 🤖 Whisper-Modelle

| Modell | Größe | Geschwindigkeit | Qualität | Empfehlung |
|--------|-------|-----------------|----------|------------|
| `tiny` | ~75 MB | Sehr schnell | Niedrig | Schnelle Tests |
| `base` | ~145 MB | Schnell | Gut | **Standard (empfohlen)** |
| `small` | ~465 MB | Mittel | Besser | Bessere Genauigkeit |
| `medium` | ~1,5 GB | Langsam | Sehr gut | Hochwertige Transkription |
| `large` | ~2,9 GB | Sehr langsam | Exzellent | Beste Qualität |

> Die Modelle werden beim ersten Verwenden automatisch in `~/.cache/whisper/` heruntergeladen.

---

## 📁 Projektstruktur

```
Reaveexx-whisper-mac-app/
├── README.md             # Diese Datei
├── requirements.txt      # Python-Abhängigkeiten
├── app.py                # Einstiegspunkt – App starten
└── src/
    ├── __init__.py
    ├── main_window.py    # PyQt6 Haupt-GUI
    ├── recorder.py       # Mikrofon-Aufnahme
    ├── transcriber.py    # Whisper-Integration
    └── utils.py          # Hilfsfunktionen
```

---

## 🐛 Fehlerbehebung

### „Mikrofon-Fehler" beim Start
- Gehe zu **Systemeinstellungen → Datenschutz & Sicherheit → Mikrofon** und erlaube dem Terminal/der App den Zugriff.

### FFmpeg nicht gefunden
```bash
brew install ffmpeg
```

### PyQt6-Fehler auf Apple Silicon (M1/M2/M3)
```bash
pip install --upgrade PyQt6 PyQt6-Qt6 PyQt6-sip
```

---

## 📄 Lizenz

MIT License – frei verwendbar und veränderbar.
