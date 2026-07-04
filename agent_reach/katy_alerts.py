# -*- coding: utf-8 -*-
"""Katy Alerts — Proactive weather, earthquake, and news alerts.

Uses:
- Weather: wttr.in (free, no API key)
- Earthquakes: USGS Earthquake API (free, no API key)
- News: agent-reach search capabilities

Default location: El Tigre, Venezuela
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
import urllib.request
import urllib.parse


@dataclass
class Alert:
    """Simple alert data class."""
    type: str  # weather, earthquake, news, reminder
    message: str
    priority: str  # low, medium, high
    timestamp: datetime
    data: Optional[dict] = None


class KatyAlerts:
    """Proactive alerts system.
    
    Checks weather, earthquakes, and news periodically.
    Default location: El Tigre, Venezuela.
    """
    
    CONFIG_FILE = Path.home() / ".agent-reach" / "katy_alerts.json"
    
    # Default location
    DEFAULT_LOCATION = "El Tigre, Anzoátegui, Venezuela"
    DEFAULT_COORDS = (8.0, -63.5)  # Lat, Lon for El Tigre
    
    # USGS Earthquake API
    USGS_API = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def __init__(self):
        self.running = False
        self.alerts = []
        self.on_alert: Optional[Callable] = None
        self.check_interval = 1800  # 30 minutes default
        self.last_check = None
        self.location = self.DEFAULT_LOCATION
        self.coords = self.DEFAULT_COORDS
        self.news_topics = []  # Topics to monitor
        self.earthquake_min_magnitude = 4.0  # Min magnitude to alert
        self.earthquake_radius_km = 500  # Radius from location
        
        # Load config
        self._load_config()
    
    def _load_config(self):
        """Load alert configuration."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.location = config.get("location", self.DEFAULT_LOCATION)
                    self.coords = tuple(config.get("coords", self.DEFAULT_COORDS))
                    self.news_topics = config.get("news_topics", [])
                    self.check_interval = config.get("check_interval", 1800)
                    self.earthquake_min_magnitude = config.get("earthquake_min_magnitude", 4.0)
                    self.earthquake_radius_km = config.get("earthquake_radius_km", 500)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save alert configuration."""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        config = {
            "location": self.location,
            "coords": list(self.coords),
            "news_topics": self.news_topics,
            "check_interval": self.check_interval,
            "earthquake_min_magnitude": self.earthquake_min_magnitude,
            "earthquake_radius_km": self.earthquake_radius_km,
        }
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def set_location(self, location: str, coords: tuple = None):
        """Set user's location for weather and earthquakes."""
        self.location = location
        if coords:
            self.coords = coords
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
        """Check weather using wttr.in."""
        try:
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
            feels_like = current.get("FeelsLikeC", "?")
            wind_kmph = current.get("windspeedKmph", "?")
            
            # Check for severe weather
            weather_code = int(current.get("weatherCode", 0))
            is_rainy = 200 <= weather_code < 400
            is_stormy = 300 <= weather_code < 400
            is_very_hot = int(temp_c) >= 35
            is_very_cold = int(temp_c) <= 10
            
            # Build message
            if is_stormy:
                message = f"Tormenta en {self.location}! {temp_c}°C, {desc}. ¡Precaución!"
                priority = "high"
            elif is_rainy:
                message = f"Lluvia en {self.location}. {temp_c}°C, {desc}. Lleva paraguas."
                priority = "medium"
            elif is_very_hot:
                message = f"Caluroso en {self.location}! {temp_c}°C (sensación {feels_like}°C). Hidrátate."
                priority = "medium"
            elif is_very_cold:
                message = f"Frío en {self.location}. {temp_c}°C. Abrígate."
                priority = "low"
            else:
                message = f"Clima en {self.location}: {temp_c}°C, {desc}, {humidity}% humedad."
                priority = "low"
            
            return Alert(
                type="weather",
                message=message,
                priority=priority,
                timestamp=datetime.now(),
                data={
                    "temp_c": temp_c,
                    "desc": desc,
                    "humidity": humidity,
                    "feels_like": feels_like,
                    "wind_kmph": wind_kmph
                }
            )
            
        except Exception as e:
            print(f"[Katy Alerts] Error al obtener clima: {e}")
            return None
    
    def check_earthquakes(self) -> list[Alert]:
        """Check recent earthquakes using USGS API."""
        alerts = []
        
        try:
            # USGS earthquake API - last 24 hours
            params = {
                "format": "geojson",
                "latitude": self.coords[0],
                "longitude": self.coords[1],
                "maxradiuskm": self.earthquake_radius_km,
                "minmagnitude": self.earthquake_min_magnitude,
                "orderby": "time",
                "limit": 10
            }
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.USGS_API}?{query_string}"
            
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Katy/1.0"}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
            
            features = data.get("features", [])
            
            for eq in features:
                props = eq.get("properties", {})
                geometry = eq.get("geometry", {})
                coordinates = geometry.get("coordinates", [0, 0, 0])
                
                magnitude = props.get("mag", 0)
                place = props.get("place", "Unknown")
                event_time = props.get("time", 0)
                event_type = props.get("type", "earthquake")
                
                # Convert timestamp
                event_dt = datetime.fromtimestamp(event_time / 1000)
                time_ago = datetime.now() - event_dt
                hours_ago = time_ago.total_seconds() / 3600
                
                # Skip old earthquakes (> 24 hours)
                if hours_ago > 24:
                    continue
                
                # Build message
                if magnitude >= 7.0:
                    priority = "critical"
                    emoji = "EARTHQUAKE CRÍTICO"
                elif magnitude >= 5.0:
                    priority = "high"
                    emoji = "Sismo fuerte"
                elif magnitude >= 4.0:
                    priority = "medium"
                    emoji = "Sismo"
                else:
                    priority = "low"
                    emoji = "Evento sísmico"
                
                depth = coordinates[2] if len(coordinates) > 2 else "?"
                
                if hours_ago < 1:
                    time_str = f"hace {int(time_ago.total_seconds() / 60)} minutos"
                else:
                    time_str = f"hace {int(hours_ago)} horas"
                
                message = f"{emoji} M{magnitude} - {place} ({time_str}). Profundidad: {depth}km"
                
                alerts.append(Alert(
                    type="earthquake",
                    message=message,
                    priority=priority,
                    timestamp=datetime.now(),
                    data={
                        "magnitude": magnitude,
                        "place": place,
                        "depth_km": depth,
                        "time": event_dt.isoformat(),
                        "coordinates": coordinates
                    }
                ))
            
            if not alerts:
                print("[Katy Alerts] No hay sismos significativos en las últimas 24h.")
            
        except Exception as e:
            print(f"[Katy Alerts] Error al verificar sismos: {e}")
        
        return alerts
    
    def check_news(self) -> list[Alert]:
        """Check news using agent-reach's search capabilities."""
        alerts = []
        
        for topic in self.news_topics:
            try:
                # For now, create a reminder
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
            
            # Check earthquakes
            earthquake_alerts = self.check_earthquakes()
            for alert in earthquake_alerts:
                if self.on_alert:
                    self.on_alert(alert)
            
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
        print(f"[Katy Alerts] Ubicación: {self.location}")
        print(f"[Katy Alerts] Sismos: radio {self.earthquake_radius_km}km, min magnitud {self.earthquake_min_magnitude}")
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
        
        earthquakes = self.check_earthquakes()
        for eq in earthquakes:
            print(f"[Katy Alerts] Sismo: {eq.message}")
        
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