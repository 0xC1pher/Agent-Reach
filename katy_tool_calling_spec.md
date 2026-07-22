# Spec v2: Katy como Agente CLI Autónomo para Pair Programming

> **Revisión completa.** Katy no es un asistente de voz con botones bonitos.
> Es un agente CLI que investiga, ejecuta y trae contexto real a tu terminal
> mientras haces pair programming.

---

## 1. La Visión (Como la Entendí)

```
Tú (programando)                          Katy (investigando en paralelo)
─────────────────                          ──────────────────────────────
"Katy, busca cómo resolver               $ katy dispatch "resolver errores
 errores de CORS en Django"               de CORS en Django"
                                          │
                                          ├─ IntentClassifier → web_search
                                          ├─ Exa search: "CORS Django fix"
                                          ├─ Obscura/Jina: lee top 3 URLs
                                          ├─ Trunca + formatea markdown
                                          │
                                          └─ stdout → tu terminal:
                                             ════════════════════════
                                             [Katy] 3 resultados relevantes:
                                             1. Settings: CORS_ALLOWED_ORIGINS...
                                             2. Middleware order matters...
                                             3. Para DRF usar corsheaders...
                                             ════════════════════════

Tú sigues codificando con esa info.
```

**Katy es un subcomando CLI más.** Se queda en la terminal. No abre ventanas. No tiene UI. Es `agent-reach katy dispatch "..."` y te devuelve resultados accionables.

---

## 2. Estado Actual vs Lo que Necesitamos

### Lo que YA funciona y se conserva

| Componente | Se conserva | Por qué |
|---|---|---|
| `agent-reach katy listen` (STT) | ✅ | Útil para voz → texto → dispatch |
| `agent-reach katy speak` (TTS) | ✅ | Opcional, leer resultados en voz alta |
| `agent-reach katy chat` (conversación) | ✅ | Se amplía para enrutar a tools |
| `katy_memory.py` (vault) | ✅ | Memoria persistente entre sesiones |
| `katy_alerts.py` (clima/sismos) | ✅ | Ya funciona como tool aislado |
| `katy_skill.py` (permisos) | ✅ | Framework de `can_do()` ya existe |
| Channels `check()` | ✅ | Verificación de qué herramientas hay |

### Lo que FALTA (el gap real)

| Gap | Descripción |
|---|---|
| **`dispatch` command** | No existe un comando que tome texto → clasifique intención → ejecute tool → devuelva resultado |
| **Tool execution layer** | Los channels no ejecutan nada, solo verifican. Necesitan `run()` que invoque los CLIs |
| **Headless browser** | Para URLs que Jina Reader no puede leer. Opciones: Obscura (Rust, ~30MB) o `browser39` |
| **Output pipeline** | Los resultados raw de subprocess vienen sucios. Falta limpiar, truncar y formatear para terminal |
| **Contexto para LLM** | El LLM recibe solo el user input. Debería recibir: user input + resultado de tool → respuesta contextualizada |

---

## 3. Arquitectura Propuesta

### Principios de diseño

1. **Todo es CLI.** Cada nuevo componente se invoca con `agent-reach katy <subcommand>`.
2. **Sin wrappers.** Las tools ejecutan los CLIs upstream directamente con `subprocess`.
3. **Sin estado server.** No daemons, no APIs REST, no puertos. Input → proceso → output → sale.
4. **Composable.** Puedes hacer `agent-reach katy dispatch "..." | grep "algo"` o pipear a otro comando.

### Nuevo flujo

```
agent-reach katy dispatch "busca en Twitter qué dicen sobre Rust 2026"
    │
    ▼
┌────────────────────────────────┐
│  IntentClassifier              │
│  (keyword + pattern matching)  │
│                                │
│  Input: "busca en Twitter      │
│          qué dicen sobre       │
│          Rust 2026"            │
│                                │
│  Match: twitter + busca        │
│  Intent: twitter_search        │
│  Query: "Rust 2026"            │
│  Confidence: 0.9               │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  ToolGate                      │
│  1. ¿Channel disponible?       │
│     twitter.check() → ok/off   │
│  2. ¿Permiso concedido?        │
│     skill.can_do("search") → ✅│
│  3. Si no → error claro        │
│     "[Katy] Twitter no está     │
│      configurado. Ejecuta:     │
│      agent-reach install       │
│      --channels=twitter"       │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  ToolExecutor                  │
│  subprocess.run(               │
│    ["twitter", "search",       │
│     "Rust 2026", "--limit=5"], │
│    capture_output=True,        │
│    timeout=30                  │
│  )                             │
│                                │
│  → stdout capturado            │
│  → limpieza + truncado         │
│  → ToolResult(data="...")      │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  ResponseFormatter             │
│  (SIN LLM si --raw)            │
│  (CON LLM si --natural)        │
│                                │
│  --raw: imprime resultado      │
│         limpio directo          │
│  --natural: pasa al LLM con    │
│     contexto para respuesta    │
│     en lenguaje natural        │
└────────────────────────────────┘
         │
         ▼
    stdout (tu terminal)
```

### Headless Browser: Cuándo y Cuál

Jina Reader (`curl https://r.jina.ai/URL`) ya está integrado y funciona para el 80% de las páginas. Para el 20% que no (SPAs pesados, anti-bot, JS-rendered), necesitas un headless browser real.

**Opciones evaluadas:**

| Herramienta | Tipo | Tamaño | Lo que hace | Viabilidad |
|---|---|---|---|---|
| **Jina Reader** | HTTP proxy | 0 bytes (remoto) | HTML → Markdown. Ya integrado en `web.py` | ✅ Ya funciona |
| **Obscura** | Rust binary | ~30MB | Headless browser + CDP + DOM→Markdown | ✅ Ideal — binario estático, sin dependencias |
| **browser39** | Rust binary | ~52MB | Fetch + render → Markdown para LLMs | ✅ Alternativa simple |
| **page-agent** (Alibaba) | JS in-page | npm package | Controla UI web con lenguaje natural | ❌ Requiere browser abierto, no es CLI |
| **agent-browser** (Vercel) | CLI daemon | Node.js | `click`, `fill`, `snapshot` via CDP | ⚠️ Requiere Node.js runtime |

**Mi recomendación:** Usar **Obscura** como fallback cuando Jina falla. Es un binario estático sin dependencias que se descarga una vez. La cadena sería:

```
web_read(url):
  1. Intentar Jina Reader (rápido, gratis)
  2. Si falla (403, timeout, JS-only) → Obscura fetch --format=markdown
  3. Si Obscura no instalado → dar instrucciones de instalación
```

> [!IMPORTANT]
> **page-agent de Alibaba NO sirve para este caso.** Es una librería JS que se inyecta dentro de una página web para controlar la UI con lenguaje natural. Requiere un navegador abierto con la página cargada. No es CLI ni headless. Es para otro tipo de proyecto.

---

## 4. Tools Concretas (Fase 1)

Cada tool es una función Python que ejecuta un subprocess y devuelve texto limpio.

### 4.1 `twitter_search(query, limit=5)`
```python
# Ejecuta: twitter search "query" --limit 5
# Requiere: twitter-cli instalado + autenticado
# Fallback: ninguno (sin twitter no hay twitter)
subprocess.run(["twitter", "search", query, "--limit", str(limit)])
```

### 4.2 `twitter_read(url)`
```python
# Ejecuta: twitter read URL
# Para tweets individuales o hilos
subprocess.run(["twitter", "read", url])
```

### 4.3 `web_read(url)`
```python
# Ya existe en web.py — Jina Reader
# Fallback: obscura fetch url --format=markdown
urllib.request.urlopen(f"https://r.jina.ai/{url}")
```

### 4.4 `web_search(query)`
```python
# Ejecuta: mcporter call exa search "query"
# Requiere: mcporter + exa configurado
subprocess.run(["mcporter", "call", "exa", "search", query])
```

### 4.5 `youtube_search(query, limit=5)`
```python
# Ejecuta: yt-dlp "ytsearch5:query" --dump-json --flat-playlist
# Devuelve títulos + URLs
subprocess.run(["yt-dlp", f"ytsearch{limit}:{query}", "--dump-json", "--flat-playlist"])
```

### 4.6 `youtube_subtitles(url)`
```python
# Ya existe en youtube.py como transcribe()
# yt-dlp + whisper
```

### 4.7 `rss_read(url)`
```python
# Nativo Python — no subprocess
import feedparser
feed = feedparser.parse(url)
# Devuelve últimas N entradas formateadas
```

### 4.8 `github_search(query)` / `github_read(repo)`
```python
# Ejecuta: gh search repos "query" --limit 5
# o: gh repo view owner/repo
subprocess.run(["gh", "search", "repos", query, "--limit", "5"])
```

### 4.9 `weather(location=None)`
```python
# Ya existe en katy_alerts.py — wttr.in
# Sin subprocess, urllib directo
```

### 4.10 `memory_search(query)`
```python
# Ya existe en katy_memory.py — búsqueda en vault
# Sin subprocess, lectura directa de archivos
```

---

## 5. Archivos a Crear/Modificar

### NUEVOS (3 archivos)

```
agent_reach/
├── tool_dispatcher.py      # IntentClassifier + dispatch logic
├── tool_executor.py        # Ejecución de subprocess + captura + limpieza
└── tool_registry.py        # Mapeo intent→channel→comando
```

### MODIFICAR (5 archivos, cambios quirúrgicos)

| Archivo | Cambio exacto |
|---|---|
| `channels/base.py` | Agregar método opcional `run(action, params) → str` |
| `channels/web.py` | Agregar fallback a Obscura si Jina falla |
| `channels/twitter.py` | Agregar `run("search", {query})` y `run("read", {url})` |
| `channels/youtube.py` | Agregar `run("search", {query})` |
| `channels/rss.py` | Agregar `run("parse", {url})` |

### MODIFICAR (3 archivos Katy, cambios en flujo)

| Archivo | Cambio exacto |
|---|---|
| `katy_llm.py` | `chat(user_input, context=None)` — acepta contexto inyectado de tools |
| `channels/katy.py` | `chat_turn()` pasa por dispatcher antes del LLM |
| `cli.py` | Agregar subcomando `katy dispatch "texto"` con flags `--raw`, `--natural`, `--verbose` |

### NO SE TOCA

| Archivo | Razón |
|---|---|
| `katy_memory.py` | Ya funciona, se usa tal cual como tool |
| `katy_alerts.py` | Ya funciona, se usa tal cual como tool |
| `katy_listener.py` | Se conserva, opcionalmente pipea a dispatch |
| `katy_skill.py` | Se conserva, `can_do()` se invoca desde dispatcher |
| `katy.yaml` | Se conserva, config de personalidad/permisos intacta |
| `config.py` | Se conserva, ya maneja credenciales |
| `doctor.py` | Se conserva, se reutiliza para verificar tools |
| `probe.py` | Se conserva, se reutiliza en tool_executor |

---

## 6. Interfaz CLI Final

```bash
# ═══════════════════════════════════════
# Modo dispatch (el core de esta spec)
# ═══════════════════════════════════════

# Búsqueda autónoma — Katy decide qué tool usar
agent-reach katy dispatch "busca qué dicen en Twitter sobre Python 4"
agent-reach katy dispatch "lee esta página https://docs.djangoproject.com/en/5.2/ref/middleware/"
agent-reach katy dispatch "qué hay nuevo en este repo https://github.com/nicobailon/mcporter"
agent-reach katy dispatch "busca tutoriales de CORS en Django"
agent-reach katy dispatch "revisa el RSS de Hacker News"

# Con flags
agent-reach katy dispatch "..." --raw          # Solo datos, sin LLM
agent-reach katy dispatch "..." --natural      # Respuesta en lenguaje natural (pasa por LLM)
agent-reach katy dispatch "..." --verbose      # Muestra qué tool eligió y por qué
agent-reach katy dispatch "..." --json         # Output JSON (para pipear a jq/scripts)

# ═══════════════════════════════════════
# Composable con pipes (pair programming)
# ═══════════════════════════════════════

# Buscar y filtrar
agent-reach katy dispatch "busca CORS Django" --raw | grep "ALLOWED"

# Buscar y guardar
agent-reach katy dispatch "lee https://example.com/api-docs" --raw > api_notes.md

# Voz → dispatch (flujo completo)
agent-reach katy listen audio.wav | agent-reach katy dispatch --stdin

# ═══════════════════════════════════════
# Los comandos existentes siguen igual
# ═══════════════════════════════════════
agent-reach katy chat                    # Chat interactivo (ahora con dispatch integrado)
agent-reach katy listen audio.wav        # STT
agent-reach katy speak "texto"           # TTS
agent-reach katy alerts --check          # Alertas
agent-reach katy vault --search "query"  # Memoria
```

---

## 7. Limitaciones que Van a Persistir (Honestidad)

| Limitación | Por qué no se puede resolver aquí |
|---|---|
| **No revisa tu correo** | No hay channel de email. Requiere IMAP/OAuth — proyecto aparte. |
| **No opera cuentas (postear, likear)** | Solo lectura. Las acciones de escritura están bloqueadas en `katy_skill.py` por diseño. |
| **No entiende instrucciones compuestas** | "Busca en Twitter Y en Reddit Y compara" → el keyword matcher no maneja multi-tool composition. Fase 2. |
| **No tiene contexto de tu código** | Katy no ve tu editor ni tus archivos abiertos. Solo ve lo que le pasas como texto. |
| **Qwen2.5-0.5B sigue siendo limitado** | La respuesta en `--natural` será funcional pero no brillante. Para mejor calidad, upgrade a 3B o usar Groq remoto. |
| **Latencia real** | `dispatch` con búsqueda web: ~3-8 segundos (red + subprocess). No es instantáneo. |

---

## 8. Estimación Revisada

| Fase | Tarea | Horas |
|---|---|---|
| 1 | `tool_dispatcher.py` — IntentClassifier (keyword matching, patterns, extracción de query) | 2.5h |
| 2 | `tool_executor.py` — subprocess runner, timeout, limpieza de output, ToolResult | 2h |
| 3 | `tool_registry.py` — mapeo intent→channel→comando, verificación con check() | 1.5h |
| 4 | Agregar `run()` en channels: twitter, youtube, rss, web (+fallback Obscura) | 3h |
| 5 | CLI: subcomando `katy dispatch` con flags --raw/--natural/--verbose/--json/--stdin | 2h |
| 6 | Modificar `katy_llm.py` para context injection + `chat_turn()` con dispatch | 1.5h |
| 7 | Tests: IntentClassifier accuracy, ToolExecutor timeout/error handling | 2h |
| **Total** | | **~14.5h** |

---

## 9. Decisión

¿Procedo con esta arquitectura? Necesito confirmar:

1. **¿Headless browser?** → ¿Instalo Obscura como fallback de Jina Reader, o prefieres otro?
2. **¿Modo default?** → ¿`--raw` (solo datos) o `--natural` (LLM humaniza)?
3. **¿Empiezo?** → Si sí, arranco por Fase 1 (IntentClassifier) y te muestro el primer archivo para que valides el approach.
