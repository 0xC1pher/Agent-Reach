# -*- coding: utf-8 -*-
"""RSS — check if feedparser is available."""

from .base import Channel


class RSSChannel(Channel):
    name = "rss"
    description = "RSS/Atom 订阅源"
    backends = ["feedparser"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return any(x in url.lower() for x in ["/feed", "/rss", ".xml", "atom"])

    def check(self, config=None):
        try:
            import feedparser  # noqa: F401
        except ImportError:
            self.active_backend = None
            return "off", "feedparser 未安装。安装：pip install feedparser"
        except Exception as e:
            # 已安装但导入期崩溃（半残安装/版本冲突）→ 重装处方
            self.active_backend = None
            return "error", f"feedparser 导入失败：{e}\n修复：pip install --force-reinstall feedparser"
        self.active_backend = self.backends[0]
        return "ok", "可读取 RSS/Atom 源"

    def run(self, action: str, params: dict) -> str:
        """Run actions for the RSS channel."""
        if action == "parse":
            url = params.get("url", "")
            return self._parse(url)
        else:
            raise NotImplementedError(f"{self.name}.run() not implemented for action '{action}'")

    def _parse(self, url: str) -> str:
        """Parse RSS/Atom feed."""
        if not hasattr(self, 'active_backend') or not self.active_backend:
            return "[Katy] RSS no está disponible"
        
        try:
            import feedparser
            feed = feedparser.parse(url)
            
            if not feed.entries:
                return "[Katy] No se encontraron entradas en el feed"
            
            result_text = f"Últimas {len(feed.entries)} entradas:\n\n"
            for entry in feed.entries[:5]:
                result_text += f"Título: {entry.title}\n"
                result_text += f"Publicado: {getattr(entry, 'published', 'Fecha desconocida')}\n"
                if hasattr(entry, 'summary'):
                    result_text += f"Resumen: {entry.summary[:200]}...\n"
                result_text += f"Enlace: {entry.link}\n\n"
            
            return result_text.strip()
        except Exception as e:
            return f"[Katy] Error parseando RSS: {str(e)}"
