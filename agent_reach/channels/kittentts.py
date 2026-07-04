# -*- coding: utf-8 -*-
"""KittenTTS — lightweight text-to-speech via KittenTTS.

KittenTTS is a small, fast TTS model that runs locally.
Install: pip install kittentts espeakng
Usage: agent-reach tts "Hello world" -o output.wav
"""

import importlib
import os
from pathlib import Path
from typing import Tuple

from .base import Channel


class KittenTTSChannel(Channel):
    name = "kittentts"
    description = "KittenTTS (texto a voz, ligero)"
    backends = ["kittentts"]
    tier = 1  # needs pip install

    VOICES = [
        "expr-voice-2-m", "expr-voice-2-f",
        "expr-voice-3-m", "expr-voice-3-f",
        "expr-voice-4-m", "expr-voice-4-f",
        "expr-voice-5-m", "expr-voice-5-f",
    ]

    def can_handle(self, url: str) -> bool:
        return False  # TTS channel — not URL-based

    def check(self, config=None):
        try:
            importlib.import_module("kittentts")
        except ImportError:
            return "off", (
                "KittenTTS no instalado. Instalar:\n"
                "  pip install kittentts espeakng\n"
                "  choco install espeak-ng"
            )

        try:
            from phonemizer.backend.espeak.espeak import EspeakWrapper
            EspeakWrapper.library()
        except Exception:
            return "error", (
                "espeak-ng no encontrado. Instalar:\n"
                "  choco install espeak-ng\n"
                "Y configurar: PHONEMIZER_ESPEAK_LIBRARY='C:\\Program Files\\eSpeak NG\\libespeak-ng.dll'"
            )

        self.active_backend = self.backends[0]
        return "ok", "KittenTTS disponible (texto a voz local)"

    def synthesize(self, text: str, output_path: str, config=None) -> str:
        """Synthesize text to audio file. Returns output path."""
        try:
            import numpy as np
            import soundfile as sf
            from kittentts import KittenTTS
        except ImportError as e:
            raise RuntimeError(f"Dependencias faltantes: {e}. Instalar: pip install kittentts soundfile")

        from agent_reach.config import Config
        cfg = config or Config()
        voice = cfg.get("kittentts_voice") or "expr-voice-2-m"
        speed = float(cfg.get("kittentts_speed") or "1.0")

        # Ensure espeak library is findable
        espeak_dll = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
        if os.path.isfile(espeak_dll) and "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ:
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = espeak_dll

        ktts = KittenTTS()
        
        # Force Spanish language for phonemizer
        ktts._phonemizer._language = "es"
        
        audio = ktts.generate(text, voice=voice, speed=speed)
        sf.write(output_path, audio, 22050)

        return output_path
