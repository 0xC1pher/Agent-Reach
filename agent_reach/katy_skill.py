# -*- coding: utf-8 -*-
"""Katy Skill — Personality, permissions, and behavior management.

This module loads the katy.yaml config and manages Katy's personality,
permissions, memory, and proactive behaviors.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

import yaml

from agent_reach.katy_memory import KatyMemory, get_katy_memory


class KatySkill:
    """Manages Katy's personality, permissions, and behavior."""
    
    CONFIG_FILE = Path(__file__).parent / "katy.yaml"
    MEMORY_DIR = Path.home() / ".agent-reach"
    MEMORY_FILE = MEMORY_DIR / "katy_memory.json"
    
    def __init__(self, vault_path: Optional[str] = None):
        self.config = self._load_config()
        self.memory = self._load_memory()
        
        # Get vault path from config if not provided
        if vault_path is None:
            vault_path = self.config.get("memory", {}).get("vault", {}).get("path", None)
        
        self.vault_memory = get_katy_memory(vault_path)
        
    def _load_config(self) -> dict:
        """Load katy.yaml config."""
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return self._default_config()
    
    def _default_config(self) -> dict:
        """Default config if katy.yaml not found."""
        return {
            "name": "Katy",
            "personality": {
                "greeting": "¡Hola! Soy Katy, tu asistente de voz.",
                "tone": "amigable",
                "humor": True,
                "brevity": "media",
            },
            "permissions": {
                "allowed": ["search", "read", "transcribe", "tts", "weather", "news"],
                "confirm": ["post", "email", "purchase", "delete"],
                "denied": ["admin", "payment", "personal_data", "execute"],
            },
            "memory": {"enabled": True, "max_turns": 20},
            "llm": {
                "system_prompt": "Eres Katy, una asistente de voz amigable.",
                "max_tokens": 512,
                "temperature": 0.7,
            },
        }
    
    def _load_memory(self) -> dict:
        """Load conversation memory."""
        if self.MEMORY_FILE.exists():
            try:
                with open(self.MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"turns": [], "user_name": None, "preferences": {}}
        return {"turns": [], "user_name": None, "preferences": {}}
    
    def _save_memory(self):
        """Save conversation memory."""
        self.MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def get_greeting(self) -> str:
        """Get Katy's greeting message."""
        return self.config.get("personality", {}).get(
            "greeting", "¡Hola! Soy Katy, tu asistente de voz."
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        base_prompt = self.config.get("llm", {}).get("system_prompt", "")
        
        # Add vault context if available
        if self.vault_memory.is_available():
            north_star = self.vault_memory.get_north_star()
            if north_star:
                # Extract current focus from North Star
                lines = north_star.split("\n")
                focus_section = []
                in_focus = False
                for line in lines:
                    if "## Current Focus" in line or "## Foco Actual" in line:
                        in_focus = True
                        continue
                    if in_focus and line.startswith("##"):
                        break
                    if in_focus and line.strip() and not line.startswith("_"):
                        focus_section.append(line.strip())
                
                if focus_section:
                    base_prompt += f"\n\nMetas actuales del usuario: {', '.join(focus_section)}"
        
        return base_prompt
    
    def get_rules(self) -> list:
        """Get behavior rules from katy.yaml."""
        return self.config.get("personality", {}).get("rules", [])
    
    def get_personality(self) -> dict:
        """Get personality settings."""
        return self.config.get("personality", {})
    
    def can_do(self, action: str) -> tuple[bool, str]:
        """Check if Katy can perform an action.
        
        Returns:
            (allowed, reason) tuple
        """
        perms = self.config.get("permissions", {})
        
        if action in perms.get("denied", []):
            return False, "Esta acción no está permitida por seguridad."
        
        if action in perms.get("confirm", []):
            return True, "Requiere confirmación del usuario."
        
        if action in perms.get("allowed", []):
            return True, "Acción permitida."
        
        return False, "Acción no reconocida."
    
    def check_wake_word(self, text: str) -> bool:
        """Check if text contains Katy's wake word."""
        wake_config = self.config.get("wake_word", {})
        if not wake_config.get("enabled", True):
            return True  # If wake word disabled, always active
        
        triggers = wake_config.get("triggers", ["hey katy", "katy"])
        text_lower = text.lower().strip()
        
        return any(trigger in text_lower for trigger in triggers)
    
    def add_conversation_turn(self, user_input: str, katy_response: str):
        """Add a turn to conversation memory."""
        max_turns = self.config.get("memory", {}).get("max_turns", 20)
        
        self.memory["turns"].append({
            "user": user_input,
            "katy": katy_response,
        })
        
        # Keep only last N turns
        if len(self.memory["turns"]) > max_turns:
            self.memory["turns"] = self.memory["turns"][-max_turns:]
        
        self._save_memory()
        
        # Also log to vault if available
        if self.vault_memory.is_available():
            self.vault_memory.add_conversation_log(user_input, katy_response)
    
    def get_conversation_context(self) -> str:
        """Get recent conversation context for the LLM."""
        turns = self.memory.get("turns", [])
        if not turns:
            return ""
        
        context = "Conversación reciente:\n"
        for turn in turns[-5:]:  # Last 5 turns
            context += f"Usuario: {turn['user']}\n"
            context += f"Katy: {turn['katy']}\n"
        
        return context
    
    def get_vault_context(self, query: str) -> str:
        """Get relevant vault context for a query."""
        if not self.vault_memory.is_available():
            return ""
        return self.vault_memory.get_context_for_query(query)
    
    def set_user_name(self, name: str):
        """Remember user's name."""
        self.memory["user_name"] = name
        self._save_memory()
    
    def get_user_name(self) -> Optional[str]:
        """Get user's name if remembered."""
        return self.memory.get("user_name")
    
    def set_preference(self, key: str, value: Any):
        """Remember a user preference."""
        if "preferences" not in self.memory:
            self.memory["preferences"] = {}
        self.memory["preferences"][key] = value
        self._save_memory()
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Get a user preference."""
        return self.memory.get("preferences", {}).get(key)
    
    def format_response(self, text: str) -> str:
        """Format response according to personality settings."""
        personality = self.config.get("personality", {})
        
        # Apply brevity setting
        brevity = personality.get("brevity", "media")
        if brevity == "corta":
            # Keep only first sentence if too long
            sentences = text.split(".")
            if len(sentences) > 1:
                text = sentences[0] + "."
        
        return text


# Global instance
_katy_skill: Optional[KatySkill] = None


def get_katy_skill() -> KatySkill:
    """Get or create KatySkill instance."""
    global _katy_skill
    if _katy_skill is None:
        _katy_skill = KatySkill()
    return _katy_skill