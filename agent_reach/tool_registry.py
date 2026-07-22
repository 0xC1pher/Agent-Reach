# -*- coding: utf-8 -*-
"""
Tool registry mapping intents to channels and commands.
"""

from typing import Dict, Any, Optional
from agent_reach.tools import ToolResult


class ToolRegistry:
    """Registry mapping intents, channels, and commands."""
    
    def __init__(self):
        self.intent_map = {
            "search": {
                "channels": {
                    "twitter": {
                        "base_intent": "search",
                        "extract_query": lambda x: self._extract_twitter_query(x),
                        "build_command": lambda query: self._build_twitter_search_command(query),
                    }
                }
            },
            "read": {
                "channels": {
                    "web": {
                        "base_intent": "read",
                        "extract_url": lambda x: self._extract_url(x),
                        "build_command": lambda url: self._build_web_read_command(url),
                    },
                    "twitter": {
                        "base_intent": "read",
                        "extract_url": lambda x: self._extract_url(x),
                        "build_command": lambda url: self._build_twitter_read_command(url),
                    }
                }
            },
            "read_twitter": {
                "channels": {
                    "twitter": {
                        "base_intent": "read",
                        "extract_url": lambda x: self._extract_url(x),
                        "build_command": lambda url: self._build_twitter_read_command(url),
                    }
                }
            },
            "search_youtube": {
                "channels": {
                    "youtube": {
                        "base_intent": "search",
                        "extract_query": lambda x: self._extract_youtube_query(x),
                        "build_command": lambda query: self._build_youtube_search_command(query),
                    }
                }
            },
            "parse_rss": {
                "channels": {
                    "rss": {
                        "base_intent": "read",
                        "extract_url": lambda x: self._extract_url(x),
                        "build_command": lambda url: self._build_rss_parse_command(url),
                    }
                }
            },
            "weather": {
                "channels": {
                    "katy_alerts": {
                        "base_intent": "weather",
                        "extract_location": lambda x: self._extract_location(x),
                        "build_command": lambda loc: self._build_weather_command(loc),
                    }
                }
            },
            "memory_search": {
                "channels": {
                    "katy_memory": {
                        "base_intent": "memory",
                        "extract_query": lambda x: self._extract_memory_query(x),
                        "build_command": lambda query: self._build_memory_search_command(query),
                    }
                }
            },
        }
    
    def get_tool_config(self, intent_name: str, channel: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration for intent and channel."""
        if intent_name in self.intent_map:
            if channel in self.intent_map[intent_name]["channels"]:
                return self.intent_map[intent_name]["channels"][channel]
        return None
    
    # Command builders
    def _build_twitter_search_command(self, query: str) -> str:
        """Build twitter search command."""
        return f"twitter search {query} --limit 5"
    
    def _build_web_read_command(self, url: str) -> str:
        """Build web read command."""
        return f"web read {url}"
    
    def _build_twitter_read_command(self, url: str) -> str:
        """Build twitter read command."""
        return f"twitter read {url}"
    
    def _build_youtube_search_command(self, query: str) -> str:
        """Build youtube search command."""
        return f"youtube search {query} --limit 5"
    
    def _build_rss_parse_command(self, url: str) -> str:
        """Build rss parse command."""
        return f"rss parse {url}"
    
    def _build_weather_command(self, location: str) -> str:
        """Build weather command."""
        return f"katy alerts --check --location {location}"
    
    def _build_memory_search_command(self, query: str) -> str:
        """Build memory search command."""
        return f"katy vault --search {query}"
    
    # Extractors
    def _extract_twitter_query(self, text: str) -> str:
        """Extract query from twitter search intent."""
        # Remove common prefixes
        text_lower = text.lower()
        if text_lower.startswith("busca en twitter"):
            return text[12:].strip()
        elif text_lower.startswith("busca qué dicen sobre"):
            return text[19:].strip()
        elif text_lower.startswith("qué dicen sobre"):
            return text[14:].strip()
        return text
    
    def _extract_url(self, text: str) -> str:
        """Extract URL from text."""
        import re
        # Find URL pattern
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else text
    
    def _extract_youtube_query(self, text: str) -> str:
        """Extract query from youtube search intent."""
        # Remove common prefixes
        text_lower = text.lower()
        if text_lower.startswith("busca en youtube"):
            return text[14:].strip()
        elif text_lower.startswith("buscar en youtube"):
            return text[17:].strip()
        return text
    
    def _extract_location(self, text: str) -> str:
        """Extract location from weather intent."""
        # Remove common prefixes
        text_lower = text.lower()
        if text_lower.startswith("clima en"):
            return text[8:].strip()
        elif text_lower.startswith("clima de"):
            return text[8:].strip()
        return text
    
    def _extract_memory_query(self, text: str) -> str:
        """Extract query from memory search intent."""
        # Remove common prefixes
        text_lower = text.lower()
        if text_lower.startswith("buscar en mi memoria"):
            return text[17:].strip()
        elif text_lower.startswith("qué dice mi memoria"):
            return text[16:].strip()
        elif text_lower.startswith("buscar en vault"):
            return text[15:].strip()
        return text