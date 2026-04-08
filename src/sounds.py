"""
sounds.py – Sound-Feedback über macOS-Systemsounds
"""

import subprocess
import threading

# Pfade zu macOS-Systemsounds
SYSTEM_SOUNDS: dict[str, str] = {
    "start": "/System/Library/Sounds/Ping.aiff",
    "stop": "/System/Library/Sounds/Pop.aiff",
    "success": "/System/Library/Sounds/Glass.aiff",
    "error": "/System/Library/Sounds/Basso.aiff",
}


def play_sound(sound_name: str) -> None:
    """Spielt einen macOS-Systemsound asynchron ab."""
    path = SYSTEM_SOUNDS.get(sound_name)
    if path:
        threading.Thread(
            target=lambda: subprocess.run(["afplay", path], check=False),
            daemon=True,
        ).start()
