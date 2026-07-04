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
    description = "Katy — asistente de voz local (Gemma 3n + KittenTTS)"
    backends = ["katy"]
    tier = 2  # needs pip install + model download

    # Model config
    STT_MODEL = "unsloth/gemma-3n-E2B-it"  # 2B effective params, ~4GB
    STT_MODEL_4BIT = "unsloth/gemma-3n-E2B-it-unsloth-bnb-4bit"  # 4-bit quantized
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
        return "ok", "Katy disponible (Gemma 3n + KittenTTS)"

    def _load_stt_model(self, config=None):
        """Load Gemma 3n model for speech understanding."""
        import torch
        from transformers import AutoProcessor, Gemma3nForConditionalGeneration

        from agent_reach.config import Config
        cfg = config or Config()

        use_4bit = cfg.get("katy_4bit", "true").lower() == "true"
        model_name = self.STT_MODEL_4BIT if use_4bit else self.STT_MODEL

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        print(f"[Katy] Cargando modelo {model_name} en {device}...")

        processor = AutoProcessor.from_pretrained(model_name)
        model = Gemma3nForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map=device,
        )

        return model, processor, device

    def _load_tts_model(self):
        """Load KittenTTS model."""
        from kittentts import KittenTTS
        return KittenTTS()

    def listen(self, audio_path: str, config=None) -> str:
        """Understand spoken audio via Gemma 3n. Returns text response."""
        import torch
        import soundfile as sf
        import numpy as np

        model, processor, device = self._load_stt_model(config)

        # Load audio
        audio, sr = sf.read(audio_path)
        if sr != 16000:
            # Resample to 16kHz
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

        # Prepare input
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio": audio.tolist()},
                    {"type": "text", "text": "Transcribe this audio accurately. If it's a question, answer it."}
                ]
            }
        ]

        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
        ).to(device)

        # Generate
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=256)

        # Decode only the new tokens
        response = processor.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        # Cleanup
        del model, processor
        if device == "cuda":
            torch.cuda.empty_cache()

        return response.strip()

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
        from agent_reach.config import Config
        
        cfg = config or Config()
        
        # Build messages with personality and context
        system_prompt = skill.get_system_prompt()
        conversation_context = skill.get_conversation_context()
        
        # Add user name if known
        user_name = skill.get_user_name()
        if user_name:
            system_prompt += f"\n\nEl usuario se llama {user_name}."
        
        # Add conversation context
        if conversation_context:
            system_prompt += f"\n\n{conversation_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        # Use Gemma 3n for response generation
        try:
            import torch
            from transformers import AutoProcessor, Gemma3nForConditionalGeneration
            
            model_name = self.STT_MODEL_4BIT if cfg.get("katy_4bit", "true").lower() == "true" else self.STT_MODEL
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            
            processor = AutoProcessor.from_pretrained(model_name)
            model = Gemma3nForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=dtype,
                device_map=device,
            )
            
            # Apply chat template
            inputs = processor.apply_chat_template(
                messages,
                tokenize=True,
                return_dict=True,
            ).to(device)
            
            # Generate response
            max_tokens = skill.config.get("llm", {}).get("max_tokens", 512)
            temperature = skill.config.get("llm", {}).get("temperature", 0.7)
            
            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                )
            
            # Decode only new tokens
            response = processor.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            # Cleanup
            del model, processor
            if device == "cuda":
                torch.cuda.empty_cache()
            
            return response.strip()
            
        except Exception as e:
            # Fallback to simple response
            return f"Tuve un problema al procesar tu solicitud: {str(e)}"
