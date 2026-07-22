# -*- coding: utf-8 -*-
"""Katy LLM — Multi-provider chat completions.

Unified interface for Groq, OpenAI, and local models.
Any model can drive Katy with the same behavior.
"""

import json
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

import requests


class Provider(Enum):
    """Supported LLM providers."""
    GROQ = "groq"
    OPENAI = "openai"
    LOCAL = "local"


@dataclass
class LLMResponse:
    """LLM response data class."""
    text: str
    model: str
    tokens_used: int
    provider: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


@dataclass
class ToolDefinition:
    """Standard tool definition for any provider."""
    name: str
    description: str
    parameters: Dict[str, Any]


class KatyLLM:
    """Multi-provider LLM for Katy.
    
    Provider priority:
    1. Groq (fast, free tier)
    2. OpenAI (if configured)
    3. Local model (fallback)
    """
    
    def __init__(self, config=None):
        from agent_reach.config import Config
        self.config = config or Config()
        self.system_prompt = self._build_system_prompt()
        self.current_provider = self._detect_provider()
        self.tools: List[ToolDefinition] = []
    
    def _detect_provider(self) -> Provider:
        """Detect which provider is available."""
        if self.config.get("groq_api_key") or os.environ.get("GROQ_API_KEY"):
            return Provider.GROQ
        if self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"):
            return Provider.OPENAI
        return Provider.LOCAL
    
    def _build_system_prompt(self) -> str:
        """Build system prompt from katy.yaml config."""
        from agent_reach.katy_skill import get_katy_skill
        skill = get_katy_skill()
        
        # Get rules from skill (loaded from katy.yaml)
        rules = skill.get_rules()
        personality = skill.get_personality()
        
        prompt = f"""
Eres {personality.get('name', 'Katy')}, una asistente de voz femenina y amigable.

Características:
- Respondo EXCLUSIVAMENTE en español
- Soy concisa pero completa
- Uso humor ligero cuando es apropiado
- Recuerdo el contexto de la conversación
- Soy honesta cuando no sé algo

Reglas importantes:
{chr(10).join(f'- {rule}' for rule in rules)}

Cuando el usuario te pida buscar, leer, o ejecutar algo, usa las herramientas disponibles.
Siempre responde en español.
"""
        
        # Add user name if known
        user_name = skill.get_user_name()
        if user_name:
            prompt += f"\nEl usuario se llama {user_name}."
        
        return prompt
    
    def register_tools(self, tools: List[ToolDefinition]):
        """Register tools for function calling."""
        self.tools = tools
    
    def _format_tools_for_groq(self) -> List[Dict[str, Any]]:
        """Format tools for Groq API."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            for tool in self.tools
        ]
    
    def _format_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Format tools for OpenAI API."""
        return self._format_tools_for_groq()  # Same format
    
    def _call_groq(self, messages: List[Dict], max_tokens: int = 512) -> Optional[LLMResponse]:
        """Call Groq API."""
        try:
            api_key = self.config.get("groq_api_key") or os.environ.get("GROQ_API_KEY")
            if not api_key:
                return None
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            
            if self.tools:
                payload["tools"] = self._format_tools_for_groq()
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]
            
            tool_calls = None
            if choice.get("message", {}).get("tool_calls"):
                tool_calls = [
                    {
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"]),
                    }
                    for tc in choice["message"]["tool_calls"]
                ]
            
            return LLMResponse(
                text=choice["message"].get("content", ""),
                model=data.get("model", "groq"),
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                provider="groq",
                tool_calls=tool_calls,
            )
            
        except Exception as e:
            print(f"[Katy LLM] Groq error: {e}")
            return None
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 512) -> Optional[LLMResponse]:
        """Call OpenAI API."""
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return None
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            }
            
            if self.tools:
                payload["tools"] = self._format_tools_for_openai()
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            
            data = response.json()
            choice = data["choices"][0]
            
            tool_calls = None
            if choice.get("message", {}).get("tool_calls"):
                tool_calls = [
                    {
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"]),
                    }
                    for tc in choice["message"]["tool_calls"]
                ]
            
            return LLMResponse(
                text=choice["message"].get("content", ""),
                model=data.get("model", "openai"),
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                provider="openai",
                tool_calls=tool_calls,
            )
            
        except Exception as e:
            print(f"[Katy LLM] OpenAI error: {e}")
            return None
    
    def _call_local(self, messages: List[Dict], max_tokens: int = 512) -> Optional[LLMResponse]:
        """Call local model (Qwen/Gemma)."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_name = "Qwen/Qwen2.5-0.5B-Instruct"
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                dtype=dtype,
                device_map=device,
                low_cpu_mem_usage=True,
            )
            
            input_text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            
            inputs = tokenizer(input_text, return_tensors="pt").to(device)
            
            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                )
            
            response = tokenizer.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            del model, tokenizer
            if device == "cuda":
                torch.cuda.empty_cache()
            
            return LLMResponse(
                text=response.strip(),
                model=model_name,
                tokens_used=0,
                provider="local",
            )
            
        except Exception as e:
            print(f"[Katy LLM] Local model error: {e}")
            return None
    
    def chat(self, user_input: str, max_tokens: int = 512) -> Optional[LLMResponse]:
        """Generate chat response using available provider."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        # Try providers in order
        providers = [
            (Provider.GROQ, self._call_groq),
            (Provider.OPENAI, self._call_openai),
            (Provider.LOCAL, self._call_local),
        ]
        
        for provider, call_fn in providers:
            if provider == self.current_provider or provider == Provider.LOCAL:
                response = call_fn(messages, max_tokens)
                if response:
                    return response
        
        return LLMResponse(
            text="Lo siento, no puedo procesar tu solicitud ahora mismo.",
            model="none",
            tokens_used=0,
            provider="none",
        )
    
    def switch_provider(self, provider: Provider):
        """Switch to a different provider."""
        self.current_provider = provider
        print(f"[Katy LLM] Switched to {provider.value}")
    
    def is_available(self) -> Dict[str, bool]:
        """Check which providers are available."""
        return {
            "groq": bool(os.environ.get("GROQ_API_KEY")),
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "local": True,  # Always available
        }


# Global instance
_llm: Optional[KatyLLM] = None


def get_llm(config=None) -> KatyLLM:
    """Get or create KatyLLM instance."""
    global _llm
    if _llm is None:
        _llm = KatyLLM(config)
    return _llm


def switch_model(provider: str):
    """Switch to a different model provider."""
    llm = get_llm()
    provider_enum = Provider(provider)
    llm.switch_provider(provider_enum)
