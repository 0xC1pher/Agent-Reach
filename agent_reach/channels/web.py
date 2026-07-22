# -*- coding: utf-8 -*-
"""Web — any URL via Jina Reader. Always available."""

import urllib.request
from .base import Channel

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


class WebChannel(Channel):
    name = "web"
    description = "任意网页"
    backends = ["Jina Reader"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return True  # Fallback — handles any URL

    def check(self, config=None):
        # 恒可用兜底渠道：无本地命令、不做网络探测（doctor 已有多个渠道触网），保持零开销
        self.active_backend = self.backends[0]
        return "ok", "通过 Jina Reader 读取任意网页（curl https://r.jina.ai/URL）"

    def read(self, url: str) -> str:
        """通过 Jina Reader 读取网页，返回 Markdown 全文。"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        jina_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(
            jina_url,
            headers={"User-Agent": _UA, "Accept": "text/plain"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")

    def run(self, action: str, params: dict) -> str:
        """Run actions for the Web channel."""
        if action == "read":
            url = params.get("url", "")
            return self.read(url)
        elif action == "search":
            query = params.get("query", "")
            return self.search(query)
        else:
            raise NotImplementedError(f"{self.name}.run() not implemented for action '{action}'")
    
    def search(self, query: str) -> str:
        """Search the web using Exa or fallback to Jina Reader."""
        import urllib.parse
        import shutil
        
        # Try Exa search first via mcporter
        try:
            import subprocess
            import os
            
            # Find mcporter executable
            mcporter_path = shutil.which("mcporter") or shutil.which("mcporter.cmd")
            if mcporter_path:
                # Use UTF-8 encoding for mcporter output
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                result = subprocess.run(
                    [mcporter_path, "call", "exa.web_search_exa", f"query: \"{query}\""],
                    capture_output=True,
                    timeout=30,
                    env=env,
                )
                if result.returncode == 0 and result.stdout:
                    # Decode with utf-8, ignore errors
                    return result.stdout.decode("utf-8", errors="ignore")
        except Exception:
            pass
        
        # Fallback: Use Jina Reader to search Google
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://s.jina.ai/{encoded_query}"
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": _UA, "Accept": "text/plain"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            return f"Error en la búsqueda: {str(e)}"
