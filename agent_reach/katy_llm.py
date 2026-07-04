# -*- coding: utf-8 -*-
"""Katy LLM — Chat completions using Groq, OpenAI, or local Gemma.

Provides a unified interface for generating responses with personality.
Uses Groq (fast, free tier) as primary, OpenAI as fallback, local Gemma as last resort.
"""

import json
from typing import Optional
from dataclasses import dataclass

import requests


@dataclass
class LLMResponse:
    """LLM response data class."""
    text: str
    model: str
    tokens_used: int
    provider: str


class KatyLLM:
    """Chat completions for Katy.
    
    Provider priority:
    1. Groq (fast, free tier)
    2. OpenAI (if configured)
    3. Local Gemma (fallback)
    """
    
    PROVIDERS = {
        "local_gemma": {
            "model": "unsloth/gemma-3n-E2B-it-4bit",
            "key_field": None,
        },
    }
    
    def __init__(self, config=None):
        from agent_reach.config import Config
        self.config = config or Config()
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with Katy's personality."""
        from agent_reach.katy_skill import get_katy_skill
        skill = get_katy_skill()
        
        prompt = skill.get_system_prompt()
        
        # Add user name if known
        user_name = skill.get_user_name()
        if user_name:
            prompt += f"\n\nEl usuario se llama {user_name}."
        
        # Add conversation context
        context = skill.get_conversation_context()
        if context:
            prompt += f"\n\n{context}"
        
        return prompt
    
    def _call_local_gemma(self, messages: list, max_tokens: int = 512) -> Optional[LLMResponse]:
        """Call local Gemma model."""
        try:
            import torch
            from transformers import AutoProcessor, Gemma3nForConditionalGeneration
            
            from agent_reach.channels.katy import KatyChannel
            ch = KatyChannel()
            
            model_name = ch.STT_MODEL_4BIT if self.config.get("katy_4bit", "true").lower() == "true" else ch.STT_MODEL
            
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
            
            # Generate
            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                )
            
            # Decode only new tokens
            text = processor.decode(
                output[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True
            )
            
            # Cleanup
            del model, processor
            if device == "cuda":
                torch.cuda.empty_cache()
            
            return LLMResponse(
                text=text.strip(),
                model=model_name,
                tokens_used=0,  # Can't track local tokens
                provider="local_gemma",
            )
            
        except Exception as e:
            print(f"[Katy LLM] Local Gemma error: {e}")
            return None
    
    def chat(self, user_input: str, max_tokens: int = 512) -> Optional[LLMResponse]:
        """Generate chat response using local Gemma model."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        response = self._call_local_gemma(messages, max_tokens)
        if response:
            return response
        
        return LLMResponse(
            text="Lo siento, no puedo procesar tu solicitud ahora mismo.",
            model="none",
            tokens_used=0,
            provider="none",
        )
    
    def is_available(self) -> dict:
        """Check which providers are available."""
        return {
            "local_gemma": True,  # Always available
        }


# Global instance
_llm: Optional[KatyLLM] = None


def get_llm(config=None) -> KatyLLM:
    """Get or create KatyLLM instance."""
    global _llm
    if _llm is None:
        _llm = KatyLLM(config)
    return _llm