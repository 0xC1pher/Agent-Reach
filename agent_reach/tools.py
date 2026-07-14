# -*- coding: utf-8 -*-
"""
ToolResult class for dispatching tools to channels.
"""

from typing import Optional, Dict, Any


class ToolResult:
    """Result of a tool execution."""
    
    def __init__(self, success: bool, data: Optional[str] = None, 
                 error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }