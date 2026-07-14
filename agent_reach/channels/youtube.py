# -*- coding: utf-8 -*-
"""YouTube — check if yt-dlp is available with JS runtime."""

import shutil

from agent_reach.probe import probe_command
from agent_reach.utils.paths import get_ytdlp_config_path, render_ytdlp_fix_command
from agent_reach.utils.text import read_utf8_text

from .base import Channel


def _has_js_runtime_config(config_path) -> bool:
    """Return whether yt-dlp config explicitly enables a JS runtime."""
    try:
        if not config_path.exists():
            return False
        return "--js-runtimes" in read_utf8_text(config_path)
    except OSError:
        return False


class YouTubeChannel(Channel):
    name = "youtube"
    description = "YouTube 视频和字幕"
    backends = ["yt-dlp"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        from urllib.parse import urlparse

        d = urlparse(url).netloc.lower()
        return "youtube.com" in d or "youtu.be" in d

    def run(self, action: str, params: dict) -> str:
        """Run actions for the YouTube channel."""
        if action == "search":
            query = params.get("query", "")
            return self._search(query)
        else:
            raise NotImplementedError(f"{self.name}.run() not implemented for action '{action}'")

    def _search(self, query: str) -> str:
        """Search for YouTube videos."""
        if not hasattr(self, 'active_backend') or not self.active_backend:
            return "[Katy] YouTube no está disponible"
        
        try:
            import subprocess
            cmd = ["yt-dlp", f"ytsearch5:{query}", "--dump-json", "--flat-playlist"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30
            )
            if result.returncode == 0:
                import json
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            video = json.loads(line)
                            videos.append(f"Título: {video.get('title', 'Sin título')}\nURL: https://youtube.com/watch?v={video.get('id', '')}\nDuración: {video.get('duration_string', 'N/A')}")
                        except:
                            continue
                return "\n\n---\n\n".join(videos)
            else:
                return f"[Katy] Error buscando en YouTube: {result.stderr}"
        except Exception as e:
            return f"[Katy] Error ejecutando búsqueda de YouTube: {str(e)}"

    def check(self, config=None):
        # 真跑 yt-dlp --version 探活，区分未装 / venv 断链 / 跑不动
        probe = probe_command("yt-dlp", ["--version"], timeout=10, package="yt-dlp")
        if probe.status == "missing":
            self.active_backend = None
            return "off", "yt-dlp 未安装。安装：pip install yt-dlp"
        if probe.status == "broken":
            self.active_backend = None
            return "error", f"yt-dlp 已安装但无法执行\n{probe.hint}"
        if not probe.ok:  # timeout / error：装了但跑不动
            self.active_backend = None
            detail = probe.hint or probe.output or probe.status
            return "error", f"yt-dlp 无法正常运行：{detail}"
        # yt-dlp 本体是活的；后面的 JS runtime/转写检查只影响 ok/warn，不影响后端归属
        self.active_backend = "yt-dlp"
        # Check JS runtime
        has_js = shutil.which("deno") or shutil.which("node")
        if not has_js:
            return "warn", (
                "yt-dlp 已安装但缺少 JS runtime（YouTube 必须）。\n"
                "  安装 Node.js 或 deno，然后运行：agent-reach install"
            )
        # Check yt-dlp config for --js-runtimes
        # Deno works out of the box; Node.js requires explicit config
        has_deno = shutil.which("deno")
        if not has_deno:
            ytdlp_config = get_ytdlp_config_path()
            if not _has_js_runtime_config(ytdlp_config):
                return "warn", (
                    f"yt-dlp 已安装但未配置 JS runtime。运行：\n  {render_ytdlp_fix_command()}"
                )
        # Surface transcription readiness so `doctor` reports it.
        msg = "可提取视频信息和字幕"
        if config is not None:
            providers = []
            if config.is_configured("groq_whisper"):
                providers.append("groq")
            if config.is_configured("openai_whisper"):
                providers.append("openai")
            if providers:
                if not shutil.which("ffmpeg"):
                    msg += "（音频转写需安装 ffmpeg）"
                else:
                    msg += f"，可转写音频（{'→'.join(providers)}）"
        return "ok", msg

    def run(self, action: str, params: dict) -> str:
        """Run actions for the YouTube channel."""
        if action == "search":
            query = params.get("query", "")
            return self._search(query)
        else:
            raise NotImplementedError(f"{self.name}.run() not implemented for action '{action}'")

    def _search(self, query: str) -> str:
        """Search for YouTube videos."""
        if not hasattr(self, 'active_backend') or not self.active_backend:
            return "[Katy] YouTube no está disponible"
        
        try:
            import subprocess
            cmd = ["yt-dlp", f"ytsearch5:{query}", "--dump-json", "--flat-playlist"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    import json
                    videos = []
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                videos.append({
                                    "title": data.get("title", ""),
                                    "url": data.get("url", ""),
                                    "uploader": data.get("uploader", ""),
                                    "duration": data.get("duration_string", data.get("duration", "")),
                                    "view_count": data.get("view_count", 0)
                                })
                            except json.JSONDecodeError:
                                pass
                    if videos:
                        result_text = "Videos encontrados:\n"
                        for i, video in enumerate(videos[:5], 1):
                            result_text += f"{i}. {video.get('title', 'Unknown')} ({video.get('url', 'No URL')})\n"
                        return result_text
                    return "[Katy] No se encontraron videos"
                return "[Katy] No se encontraron videos"
            else:
                return f"[Katy] Error buscando en YouTube: {result.stderr.strip()}"
        except Exception as e:
            return f"[Katy] Error ejecutando búsqueda en YouTube: {str(e)}"

    def transcribe(self, url: str, *, provider: str = "auto", config=None) -> str:
        """Download a YouTube video's audio and return its transcript.

        Delegates to :func:`agent_reach.transcribe.transcribe`. Imported lazily
        so the channel module stays cheap to import for users who never
        transcribe.
        """
        from agent_reach.transcribe import transcribe as _transcribe

        return _transcribe(url, provider=provider, config=config)

