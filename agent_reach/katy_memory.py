# -*- coding: utf-8 -*-
"""Katy Memory — Memoria persistente usando obsidian-mind vault.

Este módulo conecta a Katy con un vault de Obsidian como memoria persistente.
Permite leer, buscar y escribir notas en el vault para mantener contexto
entre sesiones de voz.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class KatyMemory:
    """Memoria persistente de Katy basada en obsidian-mind vault."""
    
    def __init__(self, vault_path: Optional[str] = None):
        """Inicializar con la ruta del vault.
        
        Args:
            vault_path: Ruta al vault de obsidian-mind. 
                       Si no se provee, busca en ubicaciones por defecto.
        """
        self.vault_path = self._find_vault(vault_path)
        self.brain_dir = self.vault_path / "brain" if self.vault_path else None
        self.work_dir = self.vault_path / "work" if self.vault_path else None
        
    def _find_vault(self, explicit_path: Optional[str] = None) -> Optional[Path]:
        """Encontrar el vault de obsidian-mind."""
        if explicit_path:
            # Expand ~ in path
            path = Path(os.path.expanduser(explicit_path))
            if path.exists() and (path / "brain").exists():
                return path
            return None
        
        # Buscar en ubicaciones comunes
        search_paths = [
            Path.home() / "obsidian-mind",
            Path.home() / "Desktop" / "obsidian-mind",
            Path.home() / "Documents" / "obsidian-mind",
            Path.cwd() / "obsidian-mind",
            Path.cwd().parent / "obsidian-mind",
        ]
        
        for path in search_paths:
            if path.exists() and (path / "brain").exists():
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Verificar si el vault está disponible."""
        return self.vault_path is not None and self.vault_path.exists()
    
    def get_status(self) -> dict:
        """Obtener estado del vault."""
        if not self.is_available():
            return {
                "available": False,
                "message": "Vault no encontrado. Usa 'katy memory init' para crear uno."
            }
        
        brain_files = list(self.brain_dir.glob("*.md")) if self.brain_dir else []
        work_files = list(self.work_dir.rglob("*.md")) if self.work_dir else []
        
        return {
            "available": True,
            "path": str(self.vault_path),
            "brain_notes": len(brain_files),
            "work_notes": len(work_files),
            "total_notes": len(brain_files) + len(work_files),
        }
    
    # ============================================
    # BRAIN — Conocimiento persistente
    # ============================================
    
    def read_brain(self, topic: str) -> Optional[str]:
        """Leer un tema del brain/.
        
        Args:
            topic: Nombre del tema (ej: "North Star", "Key Decisions")
        
        Returns:
            Contenido de la nota o None si no existe.
        """
        if not self.is_available():
            return None
        
        note_path = self.brain_dir / f"{topic}.md"
        if note_path.exists():
            return note_path.read_text(encoding="utf-8")
        return None
    
    def write_brain(self, topic: str, content: str, append: bool = True):
        """Escribir en un tema del brain/.
        
        Args:
            topic: Nombre del tema
            content: Contenido a escribir
            append: Si True, agrega al final. Si False, reemplaza.
        """
        if not self.is_available():
            return
        
        note_path = self.brain_dir / f"{topic}.md"
        
        if append and note_path.exists():
            existing = note_path.read_text(encoding="utf-8")
            # Agregar antes de la sección de referencia cruzada si existe
            if "## Referencia Cruzada" in existing:
                parts = existing.split("## Referencia Cruzada")
                new_content = parts[0].rstrip() + "\n\n" + content + "\n\n## Referencia Cruzada" + parts[1]
            else:
                new_content = existing.rstrip() + "\n\n" + content
            note_path.write_text(new_content, encoding="utf-8")
        else:
            # Crear nota con frontmatter
            frontmatter = f"""---
date: {datetime.now().strftime('%Y-%m-%d')}
description: "{topic} - Actualizado por Katy"
tags:
  - brain
  - katy-memory
---

"""
            note_path.write_text(frontmatter + content, encoding="utf-8")
    
    def get_north_star(self) -> Optional[str]:
        """Obtener las metas actuales (North Star)."""
        return self.read_brain("North Star")
    
    def update_north_star(self, focus: str):
        """Actualizar el foco actual en North Star."""
        content = f"""## Foco Actual

{focus}

*Actualizado por Katy el {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        self.write_brain("North Star", content, append=False)
    
    def add_decision(self, decision: str, context: str = ""):
        """Agregar una decisión a Key Decisions."""
        content = f"""### {datetime.now().strftime('%Y-%m-%d')}: {decision}

{context}

*Katy recordó esta decisión*
"""
        self.write_brain("Key Decisions", content)
    
    def add_pattern(self, pattern: str, description: str = ""):
        """Agregar un patrón a Patterns."""
        content = f"""### {pattern}

{description}

*Observado por Katy el {datetime.now().strftime('%Y-%m-%d')}*
"""
        self.write_brain("Patterns", content)
    
    def add_gotcha(self, issue: str, solution: str = ""):
        """Agregar un problema conocido a Gotchas."""
        content = f"""### {issue}

**Solución:** {solution}

*Registrado por Katy el {datetime.now().strftime('%Y-%m-%d')}*
"""
        self.write_brain("Gotchas", content)
    
    # ============================================
    # WORK — Notas de trabajo
    # ============================================
    
    def create_work_note(self, title: str, content: str, status: str = "active") -> Optional[str]:
        """Crear una nota de trabajo.
        
        Args:
            title: Título de la nota
            content: Contenido principal
            status: Estado (active, completed, archived)
        
        Returns:
            Ruta de la nota creada o None.
        """
        if not self.is_available():
            return None
        
        quarter = f"Q{(datetime.now().month - 1) // 3 + 1}-{datetime.now().year}"
        
        note_content = f"""---
date: {datetime.now().strftime('%Y-%m-%d')}
description: "{title}"
status: {status}
quarter: {quarter}
tags:
  - work-note
  - katy
---

# {title}

{content}

## Related

- [[North Star]]
"""
        
        note_path = self.work_dir / "active" / f"{title}.md"
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(note_content, encoding="utf-8")
        
        return str(note_path)
    
    def add_conversation_log(self, user_input: str, katy_response: str):
        """Registrar conversación en el vault.
        
        Crea una nota de trabajo con el log de la conversación para
        referencia futura.
        """
        if not self.is_available():
            return
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H:%M')
        
        # Buscar o crear log del día
        log_path = self.work_dir / "active" / f"Conversación {date_str}.md"
        
        if log_path.exists():
            existing = log_path.read_text(encoding="utf-8")
            new_entry = f"""
### {time_str}

**Usuario:** {user_input}

**Katy:** {katy_response}
"""
            log_path.write_text(existing.rstrip() + new_entry, encoding="utf-8")
        else:
            content = f"""---
date: {date_str}
description: "Log de conversación con Katy - {date_str}"
status: active
quarter: Q{(datetime.now().month - 1) // 3 + 1}-{datetime.now().year}
tags:
  - conversation-log
  - katy
---

# Conversación {date_str}

### {time_str}

**Usuario:** {user_input}

**Katy:** {katy_response}
"""
            log_path.write_text(content, encoding="utf-8")
    
    # ============================================
    # BÚSQUEDA
    # ============================================
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Buscar en el vault.
        
        Args:
            query: Texto a buscar
            limit: Máximo de resultados
        
        Returns:
            Lista de resultados con título, ruta y excerpt.
        """
        if not self.is_available():
            return []
        
        results = []
        query_lower = query.lower()
        
        # Buscar en brain/
        if self.brain_dir:
            for note in self.brain_dir.glob("*.md"):
                content = note.read_text(encoding="utf-8")
                if query_lower in content.lower():
                    # Extraer excerpt relevante
                    lines = content.split("\n")
                    excerpt = ""
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            start = max(0, i - 1)
                            end = min(len(lines), i + 2)
                            excerpt = "\n".join(lines[start:end])
                            break
                    
                    results.append({
                        "title": note.stem,
                        "path": str(note),
                        "excerpt": excerpt[:200],
                        "source": "brain",
                    })
        
        # Buscar en work/
        if self.work_dir:
            for note in self.work_dir.rglob("*.md"):
                if len(results) >= limit:
                    break
                try:
                    content = note.read_text(encoding="utf-8")
                    if query_lower in content.lower():
                        lines = content.split("\n")
                        excerpt = ""
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                start = max(0, i - 1)
                                end = min(len(lines), i + 2)
                                excerpt = "\n".join(lines[start:end])
                                break
                        
                        results.append({
                            "title": note.stem,
                            "path": str(note),
                            "excerpt": excerpt[:200],
                            "source": "work",
                        })
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return results[:limit]
    
    def get_context_for_query(self, query: str) -> str:
        """Obtener contexto relevante del vault para una consulta.
        
        Útil para inyectar contexto en el LLM antes de responder.
        """
        results = self.search(query, limit=3)
        
        if not results:
            return ""
        
        context = "Contexto del vault:\n\n"
        for r in results:
            context += f"**{r['title']}** ({r['source']}):\n"
            context += f"{r['excerpt']}\n\n"
        
        return context
    
    # ============================================
    # PERSONALIZACIÓN
    # ============================================
    
    def set_user_info(self, name: str, details: dict = None):
        """Guardar información del usuario."""
        content = f"""## Usuario

**Nombre:** {name}
"""
        if details:
            for key, value in details.items():
                content += f"**{key}:** {value}\n"
        
        content += f"\n*Registrado por Katy el {datetime.now().strftime('%Y-%m-%d')}*"
        
        self.write_brain("User Info", content, append=False)
    
    def get_user_info(self) -> Optional[str]:
        """Obtener información del usuario."""
        return self.read_brain("User Info")
    
    def remember_preference(self, key: str, value: str):
        """Recordar una preferencia del usuario."""
        content = f"""### {key}

{value}

*Preferencia registrada el {datetime.now().strftime('%Y-%m-%d')}*
"""
        self.write_brain("Preferences", content)
    
    # ============================================
    # ESTADÍSTICAS
    # ============================================
    
    def get_stats(self) -> dict:
        """Obtener estadísticas del vault."""
        if not self.is_available():
            return {"available": False}
        
        brain_notes = list(self.brain_dir.glob("*.md")) if self.brain_dir else []
        work_active = list((self.work_dir / "active").glob("*.md")) if self.work_dir else []
        work_archive = list((self.work_dir / "archive").rglob("*.md")) if self.work_dir else []
        
        # Contar notas con contenido real (no vacías)
        brain_with_content = 0
        for note in brain_notes:
            content = note.read_text(encoding="utf-8")
            # Contar líneas no vacías ni de frontmatter
            lines = [l for l in content.split("\n") 
                    if l.strip() and not l.startswith("---") and not l.startswith("date:") 
                    and not l.startswith("description:") and not l.startswith("tags:")]
            if len(lines) > 3:
                brain_with_content += 1
        
        return {
            "available": True,
            "vault_path": str(self.vault_path),
            "brain_notes": len(brain_notes),
            "brain_with_content": brain_with_content,
            "work_active": len(work_active),
            "work_archived": len(work_archive),
            "total_notes": len(brain_notes) + len(work_active) + len(work_archive),
        }


# Instancia global
_katy_memory: Optional[KatyMemory] = None


def get_katy_memory(vault_path: Optional[str] = None) -> KatyMemory:
    """Obtener instancia de memoria de Katy."""
    global _katy_memory
    if _katy_memory is None:
        _katy_memory = KatyMemory(vault_path)
    return _katy_memory
