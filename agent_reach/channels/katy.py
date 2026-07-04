# -*- coding: utf-8 -*-
"""Katy — Voice assistant using Gemma 3n (STT + understanding) + KittenTTS (TTS).

Katy understands spoken audio via Gemma 3n multimodal model and responds
with voice via KittenTTS. All audio is temporary — nothing saved to disk.

Usage:
    agent-reach katy listen        # Record + understand audio
    agent-reach katy speak "text"  # Generate voice response
    agent-reach katy chat          # Interactive voice loop
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

from .base import Channel


class KatyChannel(Channel):
    name = "katy"
    description = "Katy — asistente de voz local (Whisper + Gemma 2B + KittenTTS)"
    backends = ["katy"]
    tier = 2  # needs pip install + model download

    # Model config
    STT_MODEL = "base"  # Whisper model (small, fast on CPU)
    TTS_VOICE = "expr-voice-2-m"
    TTS_SPEED = 1.0

    def can_handle(self, url: str) -> bool:
        return False  # Voice channel — not URL-based

    def check(self, config=None):
        # Check torch
        try:
            import torch
        except ImportError:
            return "off", (
                "PyTorch no instalado. Instalar:\n"
                "  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
            )

        # Check transformers
        try:
            import transformers
        except ImportError:
            return "off", "transformers no instalado. Instalar: pip install transformers"

        # Check Gemma3n support
        try:
            from transformers import Gemma3nForConditionalGeneration
        except ImportError:
            return "error", "transformers no tiene soporte para Gemma 3n. Actualizar: pip install transformers>=5.5.0"

        # Check KittenTTS
        try:
            import kittentts
        except ImportError:
            return "off", "KittenTTS no instalado. Instalar: pip install kittentts"

        # Check espeak
        espeak_dll = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
        if not os.path.isfile(espeak_dll):
            return "error", "espeak-ng no instalado. Instalar: choco install espeak-ng"

        self.active_backend = self.backends[0]
        return "ok", "Katy disponible (Whisper + Gemma 2B + KittenTTS)"

    def _load_tts_model(self):
        """Load KittenTTS model."""
        from kittentts import KittenTTS
        return KittenTTS()

    def listen(self, audio_path: str, config=None) -> str:
        """Transcribe spoken audio via Whisper. Returns text."""
        import whisper

        print(f"[Katy] Cargando modelo Whisper {self.STT_MODEL}...")
        model = whisper.load_model(self.STT_MODEL)

        print("[Katy] Transcribiendo audio...")
        result = model.transcribe(audio_path, language="es", fp16=False)

        return result["text"].strip()

    def speak(self, text: str, output_path: Optional[str] = None, config=None) -> str:
        """Generate voice from text via KittenTTS. Returns audio path."""
        import os

        # Set espeak library path
        espeak_dll = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
        if os.path.isfile(espeak_dll) and "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ:
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = espeak_dll

        from agent_reach.channels.kittentts import KittenTTSChannel
        from agent_reach.config import Config

        cfg = config or Config()
        voice = cfg.get("katy_voice") or self.TTS_VOICE
        speed = float(cfg.get("katy_speed") or self.TTS_SPEED)

        # Set voice/speed in config
        cfg.set("kittentts_voice", voice)
        cfg.set("kittentts_speed", str(speed))

        ch = KittenTTSChannel()
        return ch.synthesize(text, output_path, config=cfg)

    def chat_turn(self, audio_path: str, config=None) -> tuple[str, str]:
        """Process one voice turn: listen → think → speak.
        Returns (understood_text, response_audio_path)."""
        from agent_reach.katy_skill import get_katy_skill
        
        skill = get_katy_skill()
        
        # 1. Understand audio
        understood = self.listen(audio_path, config)
        
        # 2. Check wake word (if enabled)
        if not skill.check_wake_word(understood):
            # Not addressed to Katy — ignore
            return understood, None
        
        # 3. Check permissions
        # For now, all voice commands are treated as "search" or "chat"
        action = "search"  # Default action
        allowed, reason = skill.can_do(action)
        
        if not allowed:
            response_text = reason
        else:
            # 4. Generate response using LLM with personality
            response_text = self._generate_response(understood, skill, config)
        
        # 5. Add to conversation memory
        skill.add_conversation_turn(understood, response_text)
        
        # 6. Format response according to personality
        response_text = skill.format_response(response_text)
        
        # 7. Speak response
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            response_audio = f.name
        
        self.speak(response_text, response_audio, config)
        
        return understood, response_audio
    
    def _generate_response(self, user_input: str, skill, config=None) -> str:
        """Generate response using LLM with Katy's personality."""
        from agent_reach.katy_llm import get_llm
        
        llm = get_llm(config)
        response = llm.chat(user_input)
        
        return response.text
