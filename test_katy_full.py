#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Full Katy test: record -> whisper -> LLM -> TTS -> play."""

import tempfile
import wave
import sys

import numpy as np
import sounddevice as sd

print("=== KATY VOICE ASSISTANT TEST ===")
print()

# 1. Record
print("[1/4] Grabando 5 segundos... HABLA AHORA!")
audio = sd.rec(int(5 * 16000), samplerate=16000, channels=1, dtype="int16")
sd.wait()

level = np.max(np.abs(audio.astype(float) / 32768))
print(f"  Audio level: {level:.4f}")

if level < 0.01:
    print("ERROR: Audio muy bajo. Verifica tu microfono.")
    sys.exit(1)

wav_path = tempfile.mktemp(suffix=".wav")
with wave.open(wav_path, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(audio.tobytes())

# 2. Whisper STT
print("[2/4] Transcribiendo con Whisper...")
from agent_reach.channels.katy import KatyChannel
katy = KatyChannel()
text = katy.listen(wav_path)
print(f"  Entendi: '{text}'")

if not text.strip():
    print("No se detecto voz. Intenta hablar mas fuerte.")
    sys.exit(1)

# 3. LLM Chat
print("[3/4] Pensando con Qwen2.5...")
from agent_reach.katy_llm import KatyLLM
llm = KatyLLM()
response = llm.chat(text)
print(f"  Katy dice: '{response.text}'")

# 4. TTS + Play
print("[4/4] Generando voz con KittenTTS...")
tts_path = tempfile.mktemp(suffix=".wav")
katy.speak(response.text, tts_path)
print(f"  Audio generado: {tts_path}")

print()
print("Reproduciendo respuesta...")
katy.play(tts_path)
print()
print("DONE!")
