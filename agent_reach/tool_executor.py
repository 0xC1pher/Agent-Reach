# -*- coding: utf-8 -*-
"""
Tool executor for running commands and handling subprocess execution.
"""

import subprocess
import shlex
import re
import time
from typing import Optional, Dict, Any
from agent_reach.tools import ToolResult


class ToolExecutor:
    """Execute tools via subprocess commands."""
    
    def __init__(self):
        self.probe_cache = {}
    
    def execute(self, command: str, timeout: int = 30) -> ToolResult:
        """
        Execute a command via subprocess.
        
        Args:
            command: The command to execute
            timeout: Timeout in seconds
            
        Returns:
            ToolResult with execution result
        """
        try:
            # Check if command is cached (for quick tests)
            command_key = command
            if command_key in self.probe_cache:
                cached_result = self.probe_cache[command_key]
                if time.time() - cached_result['timestamp'] < 300:  # 5 minutes
                    return ToolResult(
                        success=cached_result['success'],
                        data=cached_result['data'],
                        error=cached_result['error'],
                        metadata=cached_result['metadata']
                    )
            
            # Parse command into parts
            parts = shlex.split(command)
            
            # Execute command
            process = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            # Clean and format output
            output = self._clean_output(process.stdout)
            error = self._clean_output(process.stderr) if process.stderr else None
            
            # Determine success
            success = process.returncode == 0
            
            # Create result
            result = ToolResult(
                success=success,
                data=output if output else None,
                error=error if error and error.strip() else None,
                metadata={
                    "return_code": process.returncode,
                    "command": command,
                    "timeout": timeout,
                }
            )
            
            # Cache the result
            self.probe_cache[command_key] = {
                "success": success,
                "data": output if output else None,
                "error": error if error and error.strip() else None,
                "metadata": result.metadata,
                "timestamp": time.time()
            }
            
            return result
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"[Katy] Comando excedió el tiempo límite de {timeout} segundos: {command}",
                metadata={"timeout": timeout, "command": command}
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"[Katy] Comando no encontrado: {parts[0] if parts else command}",
                metadata={"command": command}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error ejecutando comando '{command}': {str(e)}",
                metadata={"command": command, "exception": str(e)}
            )
    
    def _clean_output(self, output: str) -> Optional[str]:
        """Clean and format command output."""
        if not output:
            return None
        
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', output)
        
        # Remove excessive whitespace
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        
        # Join lines, preserving some structure
        if len(lines) <= 10:
            return '\n'.join(lines)
        else:
            # For long outputs, show first and last few lines
            first_lines = lines[:3]
            last_lines = lines[-3:]
            return '\n'.join(first_lines + ['...', 'Contenido truncado.'] + last_lines)
    
    def execute_tool(self, channel: str, action: str, params: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool based on channel and action with parameters.
        
        Args:
            channel: The channel name
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            ToolResult with execution result
        """
        from agent_reach.channels import get_channel, ALL_CHANNELS
        
        # Check if channel exists
        channel_instance = get_channel(channel)
        if channel_instance is None:
            return ToolResult(
                success=False,
                error=f"[Katy] Canal '{channel}' no encontrado"
            )
        
        # Check if channel supports the action
        if action == "search":
            if hasattr(channel_instance, 'search'):
                return self._execute_channel_search(channel_instance, action, params)
        elif action == "read":
            if hasattr(channel_instance, 'read'):
                return self._execute_channel_read(channel_instance, action, params)
        elif action == "parse":
            if hasattr(channel_instance, 'parse'):
                return self._execute_channel_parse(channel_instance, action, params)
        elif action == "weather":
            if hasattr(channel_instance, 'weather'):
                return self._execute_channel_weather(channel_instance, action, params)
        elif action == "memory_search":
            if hasattr(channel_instance, 'memory_search'):
                return self._execute_channel_memory_search(channel_instance, action, params)
        
        # Try generic run method
        if hasattr(channel_instance, 'run'):
            try:
                result = channel_instance.run(action, params)
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            except NotImplementedError:
                pass
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"[Katy] Error ejecutando {channel}.{action}: {str(e)}"
                )
        
        return ToolResult(
            success=False,
            error=f"[Katy] Acción '{action}' no soportada por el canal '{channel}'"
        )
    
    def _execute_channel_search(self, channel_instance, action: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a channel search action."""
        if "query" not in params:
            return ToolResult(
                success=False,
                error="[Katy] Parámetro 'query' requerido para búsqueda"
            )
        
        try:
            if hasattr(channel_instance, 'search'):
                result = channel_instance.search(params["query"])
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            else:
                return ToolResult(
                    success=False,
                    error="[Katy] El canal no implementa search()"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error en {channel_instance.name}.search(): {str(e)}"
            )
    
    def _execute_channel_read(self, channel_instance, action: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a channel read action."""
        if "url" not in params:
            return ToolResult(
                success=False,
                error="[Katy] Parámetro 'url' requerido para leer"
            )
        
        try:
            if hasattr(channel_instance, 'read'):
                result = channel_instance.read(params["url"])
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            else:
                return ToolResult(
                    success=False,
                    error="[Katy] El canal no implementa read()"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error en {channel_instance.name}.read(): {str(e)}"
            )
    
    def _execute_channel_parse(self, channel_instance, action: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a channel parse action."""
        if "url" not in params:
            return ToolResult(
                success=False,
                error="[Katy] Parámetro 'url' requerido para parsear"
            )
        
        try:
            if hasattr(channel_instance, 'parse'):
                result = channel_instance.parse(params["url"])
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            else:
                return ToolResult(
                    success=False,
                    error="[Katy] El canal no implementa parse()"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error en {channel_instance.name}.parse(): {str(e)}"
            )
    
    def _execute_channel_weather(self, channel_instance, action: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a channel weather action."""
        location = params.get("location")
        if not location:
            return ToolResult(
                success=False,
                error="[Katy] Parámetro 'location' requerido para clima"
            )
        
        try:
            if hasattr(channel_instance, 'weather'):
                result = channel_instance.weather(params["location"])
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            else:
                return ToolResult(
                    success=False,
                    error="[Katy] El canal no implementa weather()"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error en {channel_instance.name}.weather(): {str(e)}"
            )
    
    def _execute_channel_memory_search(self, channel_instance, action: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a channel memory search action."""
        if "query" not in params:
            return ToolResult(
                success=False,
                error="[Katy] Parámetro 'query' requerido para buscar en memoria"
            )
        
        try:
            if hasattr(channel_instance, 'memory_search'):
                result = channel_instance.memory_search(params["query"])
                return ToolResult(
                    success=True,
                    data=result if result else None
                )
            else:
                return ToolResult(
                    success=False,
                    error="[Katy] El canal no implementa memory_search()"
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"[Katy] Error en {channel_instance.name}.memory_search(): {str(e)}"
            )