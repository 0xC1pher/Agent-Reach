# -*- coding: utf-8 -*-
"""Katy Listener — Continuous listening with wake word detection.

Simple implementation using energy-based VAD and wake word.
Reuses existing Katy channel for STT/TTS.
"""

import os
import sys
import tempfile
import threading
import time
import queue
from pathlib import Path
from typing import Optional, Callable

import numpy as np


class KatyListener:
    """Continuous listener with wake word detection.
    
    Uses energy-based voice activity detection (VAD) and
    wake word matching. Simple and KISS-compliant.
    """
    
    def __init__(self, on_wake: Optional[Callable] = None):
        self.listening = False
        self.on_wake = on_wake or self._default_wake_handler
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.chunk_size = 1024  # ~64ms at 16kHz
        self.energy_threshold = 500  # Adjustable
        self.silence_threshold = 0.5  # Seconds of silence to stop recording
        self.wake_words = ["hey katy", "katy", "oye katy", "escucha katy"]
        
        # State
        self._recording = False
        self._audio_buffer = []
        self._silence_start = None
    
    def _default_wake_handler(self, text: str, audio: np.ndarray):
        """Default wake handler — just prints."""
        print(f"[Katy Listener] Detectado: {text}")
    
    def _calculate_energy(self, audio_chunk: np.ndarray) -> float:
        """Calculate audio energy (RMS). Simple VAD."""
        return np.sqrt(np.mean(audio_chunk.astype(float) ** 2))
    
    def _detect_wake_word(self, text: str) -> bool:
        """Check if text contains wake word."""
        text_lower = text.lower().strip()
        return any(wake in text_lower for wake in self.wake_words)
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"[Katy Listener] Audio status: {status}", file=sys.stderr)
        
        # Put audio chunk in queue
        self.audio_queue.put(indata.copy())
    
    def start_listening(self):
        """Start continuous listening in background thread."""
        try:
            import sounddevice as sd
        except ImportError:
            print("[Katy Listener] sounddevice no instalado. Instalar: pip install sounddevice")
            print("[Katy Listener] Modo fallback: escucha manual con 'agent-reach katy listen'")
            return False
        
        self.listening = True
        
        def _listen_loop():
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=self.chunk_size,
                callback=self._audio_callback
            ):
                print("[Katy Listener] Escuchando... (di 'Hey Katy' para activar)")
                
                while self.listening:
                    try:
                        audio_chunk = self.audio_queue.get(timeout=0.1)
                        self._process_chunk(audio_chunk)
                    except queue.Empty:
                        continue
        
        # Start in daemon thread
        thread = threading.Thread(target=_listen_loop, daemon=True)
        thread.start()
        
        return True
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.listening = False
        print("[Katy Listener] Detenido.")
    
    def _process_chunk(self, audio_chunk: np.ndarray):
        """Process an audio chunk."""
        energy = self._calculate_energy(audio_chunk)
        
        if energy > self.energy_threshold:
            # Speech detected
            if not self._recording:
                self._recording = True
                self._audio_buffer = [audio_chunk]
                self._silence_start = None
            else:
                self._audio_buffer.append(audio_chunk)
                self._silence_start = None
        else:
            # Silence
            if self._recording:
                if self._silence_start is None:
                    self._silence_start = time.time()
                elif time.time() - self._silence_start > self.silence_threshold:
                    # End of speech — process
                    self._process_speech()
    
    def _process_speech(self):
        """Process recorded speech."""
        if not self._audio_buffer:
            return
        
        # Concatenate audio
        audio = np.concatenate(self._audio_buffer)
        
        # Reset state
        self._recording = False
        self._audio_buffer = []
        self._silence_start = None
        
        # Save to temp file
        import soundfile as sf
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            sf.write(f.name, audio, self.sample_rate)
        
        try:
            # Use existing Katy channel for STT
            from agent_reach.channels.katy import KatyChannel
            ch = KatyChannel()
            
            text = ch.listen(temp_path)
            
            if self._detect_wake_word(text):
                # Wake word detected!
                print(f"[Katy Listener] ¡Desperté! {text}")
                self.on_wake(text, audio)
        
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def listen_once(self, audio_path: str) -> str:
        """Listen to a single audio file (manual mode)."""
        from agent_reach.channels.katy import KatyChannel
        ch = KatyChannel()
        return ch.listen(audio_path)


# Global instance
_listener: Optional[KatyListener] = None


def get_listener() -> KatyListener:
    """Get or create KatyListener instance."""
    global _listener
    if _listener is None:
        _listener = KatyListener()
    return _listener


def start_continuous_listening(on_wake: Optional[Callable] = None) -> bool:
    """Start continuous listening."""
    listener = get_listener()
    if on_wake:
        listener.on_wake = on_wake
    return listener.start_listening()


def stop_continuous_listening():
    """Stop continuous listening."""
    listener = get_listener()
    listener.stop_listening()