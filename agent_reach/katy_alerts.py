# -*- coding: utf-8 -*-
"""Katy Alerts — Proactive weather and news alerts.

Simple implementation using web scraping.
Reuses agent-reach's existing capabilities.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class Alert:
    """Simple alert data class."""
    type: str  # weather, news, reminder
    message: str
    priority: str  # low, medium, high
    timestamp: datetime
    data: Optional[dict] = None


class KatyAlerts:
    """Proactive alerts system.
    
    Checks weather and news periodically.
    Simple polling-based implementation.
    """
    
    CONFIG_FILE = Path.home() / ".agent-reach" / "katy_alerts.json"
    
    def __init__(self):
        self.running = False
        self.alerts = []
        self.on_alert: Optional[Callable] = None
        self.check_interval = 3600  # 1 hour default
        self.last_check = None
        self.location = None  # User's location
        self.news_topics = []  # Topics to monitor
        
        # Load config
        self._load_config()
    
    def _load_config(self):
        """Load alert configuration."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.location = config.get("location")
                    self.news_topics = config.get("news_topics", [])
                    self.check_interval = config.get("check_interval", 3600)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save alert configuration."""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "location": self.location,
            "news_topics": self.news_topics,
            "check_interval": self.check_interval,
        }
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def set_location(self, location: str):
        """Set user's location for weather."""
        self.location = location
        self._save_config()
        print(f"[Katy Alerts] Ubicación: {location}")
    
    def add_news_topic(self, topic: str):
        """Add a news topic to monitor."""
        if topic not in self.news_topics:
            self.news_topics.append(topic)
            self._save_config()
            print(f"[Katy Alerts] Tema agregado: {topic}")
    
    def remove_news_topic(self, topic: str):
        """Remove a news topic."""
        if topic in self.news_topics:
            self.news_topics.remove(topic)
            self._save_config()
            print(f"[Katy Alerts] Tema removido: {topic}")
    
    def check_weather(self) -> Optional[Alert]:
        """Check weather using web scraping."""
        if not self.location:
            return None
        
        try:
            # Use wttr.in (simple weather API)
            import urllib.request
            import urllib.parse
            
            location_encoded = urllib.parse.quote(self.location)
            url = f"https://wttr.in/{location_encoded}?format=j1"
            
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Katy/1.0"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Extract current conditions
            current = data.get("current_condition", [{}])[0]
            temp_c = current.get("temp_C", "?")
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
            humidity = current.get("humidity", "?")
            
            # Check for rain/snow
            weather_code = int(current.get("weatherCode", 0))
            is_rainy = 200 <= weather_code < 400  # Rough rain detection
            is_snowy = 300 <= weather_code < 400  # Rough snow detection
            
            # Build message
            if is_rainy:
                message = f"¡Llueve en {self.location}! {temp_c}°C, {desc}. Lleva paraguas."
                priority = "high"
            elif is_snowy:
                message = f"¡Nieve en {self.location}! {temp_c}°C, {desc}. Abrígate bien."
                priority = "high"
            else:
                message = f"Clima en {self.location}: {temp_c}°C, {desc}, {humidity}% humedad."
                priority = "low"
            
            return Alert(
                type="weather",
                message=message,
                priority=priority,
                timestamp=datetime.now(),
                data={"temp_c": temp_c, "desc": desc, "humidity": humidity}
            )
            
        except Exception as e:
            print(f"[Katy Alerts] Error al obtener clima: {e}")
            return None
    
    def check_news(self) -> list[Alert]:
        """Check news using agent-reach's search capabilities."""
        alerts = []
        
        for topic in self.news_topics:
            try:
                # Use agent-reach's Exa search
                import subprocess
                result = subprocess.run(
                    ["agent-reach", "doctor", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # For now, just create a reminder
                # In future, integrate with actual news API
                alerts.append(Alert(
                    type="news",
                    message=f"Noticias sobre '{topic}': (verificar manualmente)",
                    priority="medium",
                    timestamp=datetime.now(),
                    data={"topic": topic}
                ))
                
            except Exception as e:
                print(f"[Katy Alerts] Error al buscar noticias: {e}")
        
        return alerts
    
    def _check_loop(self):
        """Background check loop."""
        while self.running:
            # Check weather
            weather_alert = self.check_weather()
            if weather_alert and self.on_alert:
                self.on_alert(weather_alert)
            
            # Check news
            news_alerts = self.check_news()
            for alert in news_alerts:
                if self.on_alert:
                    self.on_alert(alert)
            
            self.last_check = datetime.now()
            
            # Sleep until next check
            time.sleep(self.check_interval)
    
    def start(self, on_alert: Optional[Callable] = None):
        """Start proactive alerts."""
        if self.running:
            print("[Katy Alerts] Ya está ejecutándose.")
            return
        
        self.running = True
        if on_alert:
            self.on_alert = on_alert
        
        # Start in daemon thread
        thread = threading.Thread(target=self._check_loop, daemon=True)
        thread.start()
        
        print(f"[Katy Alerts] Iniciado. Verificando cada {self.check_interval//60} minutos.")
        if self.location:
            print(f"[Katy Alerts] Ubicación: {self.location}")
        if self.news_topics:
            print(f"[Katy Alerts] Temas: {', '.join(self.news_topics)}")
    
    def stop(self):
        """Stop proactive alerts."""
        self.running = False
        print("[Katy Alerts] Detenido.")
    
    def check_now(self):
        """Force immediate check."""
        print("[Katy Alerts] Verificando ahora...")
        
        weather = self.check_weather()
        if weather:
            print(f"[Katy Alerts] Clima: {weather.message}")
        
        news = self.check_news()
        for alert in news:
            print(f"[Katy Alerts] Noticias: {alert.message}")


# Global instance
_alerts: Optional[KatyAlerts] = None


def get_alerts() -> KatyAlerts:
    """Get or create KatyAlerts instance."""
    global _alerts
    if _alerts is None:
        _alerts = KatyAlerts()
    return _alerts


def start_proactive_alerts(on_alert: Optional[Callable] = None):
    """Start proactive alerts."""
    alerts = get_alerts()
    alerts.start(on_alert)


def stop_proactive_alerts():
    """Stop proactive alerts."""
    alerts = get_alerts()
    alerts.stop()