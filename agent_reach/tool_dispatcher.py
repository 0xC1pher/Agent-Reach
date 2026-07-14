# -*- coding: utf-8 -*-
"""
Tool dispatcher for Katy's tool calling system.

This module provides the main interface for dispatching user requests to tools,
following the flow: IntentClassifier → ToolGate → ToolExecutor.
"""

import re
from typing import Optional, Tuple, List, Dict, Any
from .tool_executor import ToolExecutor
from .tools import ToolResult


class IntentClassifier:
    """
    Classifies user input into intents and extracts relevant information.
    
    Uses pattern matching and keywords to determine what the user wants to do.
    """
    
    # Intent patterns with channel and action mapping
    # ORDER MATTERS: More specific patterns first (YouTube before Twitter)
    INTENT_PATTERNS = {
        # YouTube patterns (MUST come before Twitter because "busca en" is common)
        "youtube_search": {
            "patterns": [
                r"(?:busca|search|look|encuentra|find).+(?:en|on)\s+youtube",
                r"youtube.+(?:busca|search|look|encuentra|find)",
                r"(?:tutorial|tutoriales|how.+to|cómo).+(?:en|on)\s+youtube",
                r"(?:qué.+dicen|what.+say|reviews|opiniones).+(?:en|on)\s+youtube",
                r"(?:busca|search).+(?:video|videos).+(?:en|on)\s+youtube",
            ],
            "channel": "youtube",
            "action": "search",
            "extract": "query",
        },
        "youtube_read": {
            "patterns": [
                r"(?:lee|read|abre|open|mira|see).+(?:video|youtube).*(?:youtube\.com|youtu\.be)",
                r"https?://(?:youtube\.com|youtu\.be)/\S+",
            ],
            "channel": "youtube",
            "action": "read",
            "extract": "url",
        },
        # Twitter/X patterns (after YouTube)
        "twitter_search": {
            "patterns": [
                r"(?:busca|search|look|encuentra|find).+(?:en|on)\s+(?:twitter|x|tweet)",
                r"(?:twitter|x|tweet).+(?:busca|search|look|encuentra|find)",
                r"(?:opiniones|opinions|reviews|comentarios|comments).+(?:en|on|twitter|x)",
            ],
            "channel": "twitter",
            "action": "search",
            "extract": "query",
        },
        "twitter_read": {
            "patterns": [
                r"(?:lee|read|abre|open|mira|see).+(?:tweet|post|thread|url).*(?:twitter|x\.com)",
                r"https?://(?:twitter|x)\.com/\S+",
            ],
            "channel": "twitter",
            "action": "read",
            "extract": "url",
        },
        # RSS patterns
        "rss_parse": {
            "patterns": [
                r"(?:revisa|check|parse|lee|read).+(?:rss|feed|atom)",
                r"(?:rss|feed|atom).+(?:de|from|para|for)",
                r"(?:noticias|news|articles|artículos).+(?:rss|feed)",
            ],
            "channel": "rss",
            "action": "parse",
            "extract": "url",
        },
        # Web patterns
        "web_read": {
            "patterns": [
                r"(?:lee|read|abre|open|extrae|extract|obtén|get).+(?:página|page|artículo|article|contenido|content|url)",
                r"(?:qué|what).+(?:dice|says|dice|contiene|contains).+(?:url|página|page)",
                r"https?://(?!twitter|x\.com|youtube|youtu\.be)\S+",
            ],
            "channel": "web",
            "action": "read",
            "extract": "url",
        },
        "web_search": {
            "patterns": [
                r"(?:busca|search|look|encuentra|find|investiga|research).+(?:en|on)\s+(?:internet|web|google)",
                r"(?:qué|what).+(?:hay|there is|exist|existe).+(?:sobre|about|respecto)",
                r"(?:información|info|information|datos|data).+(?:sobre|about|de|de)",
            ],
            "channel": "web",
            "action": "search",
            "extract": "query",
        },
        # Memory patterns
        "memory_search": {
            "patterns": [
                r"(?:busca|search|encuentra|find|recuerda|remember).+(?:en|in|mi)?\s*(?:memoria|memory|vault|obsidian)",
                r"(?:qué|what).+(?:sé|know|tengo|have).+(?:sobre|about|de)",
                r"(?:contexto|context).+(?:de|from|sobre|about)",
            ],
            "channel": "memory",
            "action": "search",
            "extract": "query",
        },
        # Weather patterns
        "weather": {
            "patterns": [
                r"(?:clima|weather|tiempo|temperatura|temperature).+(?:en|in|de|for|para)",
                r"(?:hace|is|está).+(?:frío|calor|caliente|cold|hot|warm|lluvia|rain|soleado|sunny)",
                r"(?:va a llover|will rain|pronóstico|forecast)",
            ],
            "channel": "weather",
            "action": "get",
            "extract": "location",
        },
        # Calculate patterns
        "calculate": {
            "patterns": [
                r"(?:calcula|calculate|cuánto es|how much is|suma|add|resta|subtract|multiplica|multiply|divide)",
                r"\d+\s*[\+\-\*\/\^]\s*\d+",
            ],
            "channel": "calculator",
            "action": "calculate",
            "extract": "expression",
        },
        # Memory operations
        "memory_store": {
            "patterns": [
                r"(?:recuerda|remember|guarda|save|almacena|store).+(?:que|that|el|la|los|las)",
                r"(?:mi|my).+(?:nombre|name|es|is|soy|am).+\w+",
            ],
            "channel": "memory",
            "action": "store",
            "extract": "content",
        },
    }
    
    def classify(self, user_input: str) -> Tuple[str, str, str, Optional[str]]:
        """
        Classify user input into intent, channel, action, and extracted query.
        
        Args:
            user_input: The user's request
            
        Returns:
            Tuple of (intent, channel, action, extracted_query)
        """
        user_input_lower = user_input.lower().strip()
        
        # Check each intent pattern
        for intent_name, intent_config in self.INTENT_PATTERNS.items():
            for pattern in intent_config["patterns"]:
                if re.search(pattern, user_input_lower):
                    # Extract the relevant part
                    extracted = self._extract_from_match(
                        user_input, intent_config["extract"], pattern
                    )
                    return (
                        intent_name,
                        intent_config["channel"],
                        intent_config["action"],
                        extracted,
                    )
        
        # Default: unknown intent
        return ("unknown", "unknown", "unknown", None)
    
    def _extract_from_match(
        self, user_input: str, extract_type: str, pattern: str
    ) -> Optional[str]:
        """Extract relevant information based on type."""
        user_input_lower = user_input.lower()
        
        # Try to extract URL first
        url_match = re.search(r"https?://\S+", user_input)
        if url_match:
            return url_match.group(0)
        
        # Extract based on type
        if extract_type == "query":
            # Remove common prefixes/suffixes
            query = user_input
            for remove in [
                "busca en", "search on", "look for", "encuentra en",
                "qué dicen en", "what says on", "en twitter", "on twitter",
                "en youtube", "on youtube", "en internet", "on internet",
                "sobre", "about", "de", "for", "para",
            ]:
                query = query.replace(remove, "")
            return query.strip()
        
        elif extract_type == "location":
            # Extract location after prepositions
            loc_match = re.search(
                r"(?:en|in|de|for|para)\s+(.+?)(?:\?|$)", user_input, re.IGNORECASE
            )
            if loc_match:
                return loc_match.group(1).strip()
            return None
        
        elif extract_type == "expression":
            # Extract mathematical expression
            expr_match = re.search(r"[\d\.\s\+\-\*\/\^\(\)]+", user_input)
            if expr_match:
                return expr_match.group(0).strip()
            return None
        
        elif extract_type == "content":
            # Extract the content to remember
            content_match = re.search(
                r"(?:recuerda|remember|guarda|save|almacena|store)\s+(?:que\s+|that\s+)?(.+)",
                user_input,
                re.IGNORECASE,
            )
            if content_match:
                return content_match.group(1).strip()
            return None
        
        return user_input


class ToolGate:
    """
    Checks if a tool is available and has the necessary permissions.
    """
    
    # Tools that require confirmation
    CONFIRM_REQUIRED = {"post", "email", "purchase", "delete", "share"}
    
    # Tools that are always denied
    ALWAYS_DENIED = {"admin", "payment", "personal_data", "execute"}
    
    def __init__(self, config=None):
        from agent_reach.config import Config
        self.config = config or Config()
        self._load_permissions()
    
    def _load_permissions(self):
        """Load permissions from katy.yaml."""
        try:
            from agent_reach.katy_skill import get_katy_skill
            skill = get_katy_skill()
            perms = skill.config.get("permissions", {})
            self.allowed = set(perms.get("allowed", []))
            self.confirm = set(perms.get("confirm", []))
            self.denied = set(perms.get("denied", []))
        except Exception:
            # Default permissions
            self.allowed = {"search", "read", "transcribe", "tts", "weather", "news"}
            self.confirm = {"post", "email", "purchase", "delete", "share"}
            self.denied = {"admin", "payment", "personal_data", "execute"}
    
    def check(self, channel: str, action: str) -> Tuple[bool, str]:
        """
        Check if the tool is allowed.
        
        Args:
            channel: The tool channel (e.g., "twitter", "web")
            action: The action to perform (e.g., "search", "read")
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check if channel is denied
        if channel in self.denied:
            return False, f"El canal '{channel}' no está permitido por seguridad."
        
        # Check if action is denied
        if action in self.denied:
            return False, f"La acción '{action}' no está permitida por seguridad."
        
        # Check if action requires confirmation
        if action in self.confirm:
            return True, f"La acción '{action}' requiere confirmación del usuario."
        
        # Check if action is allowed
        if action in self.allowed or channel in self.allowed:
            return True, "Acción permitida."
        
        # Default: allow (for now)
        return True, "Acción permitida."


class ToolDispatcher:
    """
    Main dispatcher for Katy's tool calling system.
    
    This class orchestrates the complete tool calling workflow:
    1. IntentClassifier analyzes user input
    2. ToolGate checks if the tool is available and has permissions
    3. ToolExecutor executes the appropriate tool
    4. ResponseFormatter formats the output
    
    Examples:
        dispatcher = ToolDispatcher()
        result = dispatcher.dispatch("busca en Twitter qué dicen sobre Python 4")
        result = dispatcher.dispatch("lee https://docs.djangoproject.com", raw=True)
    """
    
    def __init__(self, config=None):
        from agent_reach.config import Config
        self.config = config or Config()
        self.intent_classifier = IntentClassifier()
        self.tool_gate = ToolGate(self.config)
        self.tool_executor = ToolExecutor()
        # Initialize subprocess command cache
        self._subprocess_cache = {}
    
    def dispatch(self, user_input: str, **kwargs) -> ToolResult:
        """
        Dispatch a user request to the appropriate tool.
        
        Args:
            user_input: The user's request/command
            **kwargs: Additional options:
                - raw: Output raw data only (skip LLM)
                - natural: Format natural language response
                - json: Output JSON format
                - verbose: Show what Katy is doing
                - location: Location for weather requests
                
        Returns:
            ToolResult containing the execution result
        """
        # Extract options
        raw = kwargs.get('raw', False)
        natural = kwargs.get('natural', False)
        json_output = kwargs.get('json', False)
        verbose = kwargs.get('verbose', False)
        
        # Step 1: Classify intent
        if verbose:
            print(f"[Katy] Analizando: '{user_input}'")
        
        intent, channel, action, extracted_query = self.intent_classifier.classify(user_input)
        
        if verbose:
            print(f"[Katy] Acción detectada: {intent} -> {channel}.{action}")
            if extracted_query:
                print(f"[Katy] Query/query: {extracted_query}")
        
        if intent == "unknown":
            error_msg = f"[Katy] No entiendo qué quieres decir: {user_input}\n"
            error_msg += "[Katy] Intenta con: 'busca en Twitter qué dicen sobre [tópico]', "
            error_msg += "'lee [url]', 'busca en YouTube tutoriales de [tópico]', "
            error_msg += "'revisa el RSS [url]', 'clima [lugar]', o 'buscar en mi memoria [consulta]'"
            
            return ToolResult(
                success=False,
                error=error_msg,
                metadata={
                    "intent": intent,
                    "user_input": user_input,
                    "extracted_query": None,
                }
            )
        
        # Step 2: Check permissions
        is_allowed, reason = self.tool_gate.check(channel, action)
        
        if not is_allowed:
            return ToolResult(
                success=False,
                error=reason,
                metadata={
                    "intent": intent,
                    "channel": channel,
                    "action": action,
                    "user_input": user_input,
                    "permission_checked": True,
                }
            )
        
        # Step 3: Prepare parameters
        params = {}
        if action in ["search", "parse", "memory_search", "get"]:
            params["query"] = extracted_query
        elif action == "read":
            params["url"] = extracted_query
        elif action == "weather":
            params["location"] = extracted_query or kwargs.get('location', 'barcelona')
        elif action == "calculate":
            params["expression"] = extracted_query
        elif action == "store":
            params["content"] = extracted_query
        
        # Add limit for search actions
        if action == "search":
            params["limit"] = 5
        
        if verbose:
            print(f"[Katy] Ejecutando {channel}.{action} con params: {params}")
        
        # Step 4: Execute tool
        tool_result = self.tool_executor.execute_tool(channel, action, params)
        
        if tool_result.success and verbose:
            print(f"[Katy] Tool executed successfully")
            if tool_result.data:
                print(f"[Katy] Resultado: {len(tool_result.data)} caracteres")
        elif not tool_result.success and verbose:
            print(f"[Katy] Tool execution failed: {tool_result.error}")
        
        # Step 5: Format response
        if not raw:
            # If natural language requested or result is long
            if natural or (tool_result.data and len(tool_result.data) > 200):
                # In a real implementation, this would call the LLM with context
                # For now, just return the raw result with a note
                if tool_result.data:
                    formatted = f"[Katy] Encontre {action} para: '{extracted_query or user_input}'\n\n"
                    formatted += tool_result.data[:500] + "..." if len(tool_result.data) > 500 else tool_result.data
                    return ToolResult(
                        success=True,
                        data=formatted,
                        metadata={
                            **tool_result.metadata,
                            "intent": intent,
                            "channel": channel,
                            "action": action,
                            "formatted": True,
                        }
                    )
        
        if json_output:
            import json
            try:
                json_data = {
                    "success": tool_result.success,
                    "data": tool_result.data,
                    "error": tool_result.error,
                    "metadata": tool_result.metadata,
                    "intent": intent,
                    "channel": channel,
                    "action": action,
                }
                return ToolResult(
                    success=True,
                    data=json.dumps(json_data, ensure_ascii=False, indent=2),
                    metadata={"output_format": "json"}
                )
            except Exception as e:
                # Fallback to regular text
                return tool_result
        
        return tool_result
    
    def dispatch_raw(self, user_input: str) -> ToolResult:
        """
        Dispatch with raw output only (no LLM).
        
        Args:
            user_input: The user's request
            
        Returns:
            ToolResult with raw data
        """
        return self.dispatch(user_input, raw=True)
    
    def dispatch_verbose(self, user_input: str) -> ToolResult:
        """
        Dispatch with verbose output (shows what's being done).
        
        Args:
            user_input: The user's request
            
        Returns:
            ToolResult with verbose output
        """
        return self.dispatch(user_input, verbose=True)
    
    def dispatch_json(self, user_input: str) -> ToolResult:
        """
        Dispatch with JSON output format.
        
        Args:
            user_input: The user's request
            
        Returns:
            ToolResult with JSON data
        """
        return self.dispatch(user_input, json=True)
