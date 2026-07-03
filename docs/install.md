# Agent Reach — Guía de instalación

## Para humanos

Copia esto para tu AI Agent:

```
Instala Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

> 🛡️ **¿Preocupado por la seguridad?** Usa el modo seguro — no instala paquetes del sistema automáticamente:
> ```
> Instala Agent Reach (modo seguro): https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> Usa el parámetro --safe al instalar
> ```

---

## Para AI Agents

### Objetivo

Instalar Agent Reach y todas las herramientas upstream para que el Agent del usuario tenga acceso completo a internet. Después de la instación, usarás las herramientas upstream directamente (OpenCLI, twitter-cli, bili-cli, rdt-cli, yt-dlp, mcporter, gh CLI, etc.) — Agent Reach es el selector, instalador, verificador de salud y enrutador, nunca un wrapper.

### ⚠️ Límites

Al arreglar problemas, mantente dentro de estos límites:

- **NO ejecutes** comandos con `sudo` a menos que el usuario lo haya aprobado explícitamente
- **NO modifiques** archivos del sistema fuera de `~/.agent-reach/`
- **NO instales** paquetes no listados en esta guía
- **NO desactives** firewalls, configuraciones de seguridad o protecciones del sistema
- **NO clones** repos, crees archivos o ejecutes comandos dentro del directorio de trabajo del agent
- Si algo requiere permisos elevados, **dile al usuario** qué se necesita y deja que decida

### 📁 Reglas de directorios

Todos los archivos de Agent Reach van en directorios dedicados — **nunca en el directorio de trabajo del agent**:

| Propósito | Directorio | Ejemplo |
|-----------|-----------|---------|
| Config y tokens | `~/.agent-reach/` | `~/.agent-reach/config.json` |
| Repos de herramientas upstream | `~/.agent-reach/tools/` | `~/.agent-reach/tools/xiaoyuzhou/` |
| Archivos temporales | `/tmp/` | `/tmp/yt-dlp-output/` |
| Skills | `~/.openclaw/skills/agent-reach/` | SKILL.md |

**¿Por qué?** Si clonas repos o creas archivos en el directorio de trabajo, contaminas el directorio del proyecto del usuario y puedes romper su agent con el tiempo. Mantén el directorio de trabajo limpio.

### Paso 1: Instalar lo básico

```bash
# Recomendado: pipx (lo más sencillo)
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto

# Si tu Python viene de Homebrew / tienes PEP 668 (externally-managed-environment)
# Usa un entorno virtual:
python3 -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/bin/activate
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```

> 💡 **¿Windows / alias de Python de Microsoft Store?**
> Si `python3 --version` abre Microsoft Store, o `where python3` apunta a
> `...\AppData\Local\Microsoft\WindowsApps\python3.exe`, significa que `python3` es un alias
> de Store de Windows, no una instalación de Python real. Usa Python Launcher `py -3`, o el
> `python.exe` en tu directorio de instalación real.
>
> Ejemplo PowerShell:
> ```powershell
> py -3 -m venv $env:USERPROFILE\.agent-reach-venv
> $env:USERPROFILE\.agent-reach-venv\Scripts\Activate.ps1
> python -m pip install https://github.com/Panniantong/agent-reach/archive/main.zip
> agent-reach install --env=auto
> ```

Esto instala la infraestructura central (gh CLI, Node.js, mcporter, búsqueda Exa, configuración de yt-dlp) y activa estos canales de cero configuración:

- Web (Jina Reader), YouTube, GitHub, RSS, Búsqueda Exa, V2EX, Bilibili (básico)

> 💡 **¿macOS / Homebrew Python muestra `externally-managed-environment`?**
> Esto es protección PEP 668, no un problema de Agent Reach. Prioriza `pipx install ...`, o crea un `venv` primero.

**Modo seguro / Dry run:**

```bash
agent-reach install --env=auto --safe      # Solo verifica, sin auto-instalación
agent-reach install --env=auto --dry-run   # Previsualiza qué se haría
```

### Paso 2: Preguntar al usuario qué canales opcionales quiere

Después de instalar lo básico, **pregunta al usuario** qué canales adicionales necesita. Presenta esta lista:

> ¡Los canales básicos están instalados! Ahora puedes buscarme en la web, ver YouTube, leer GitHub, etc.
>
> Estos son los canales opcionales, ¿cuáles necesitas?
>
> - 🌟 **OpenCLI** (recomendado para escritorio) — Una instalación, desbloquea Xiaohongshu/Reddit/Facebook/Instagram/subtítulos de Bilibili/respaldo de Twitter (reutiliza login del navegador, cero configuración; solo haz clic una vez en "Añadir extensión" en Chrome)
> - 🐦 **Twitter/X** — Buscar tweets, ver timeline (necesita Cookie de login)
> - 📈 **Xueqiu** — Cotizaciones, posts populares (necesita Cookie de login)
> - 🎙️ **Xiaoyuzhou Podcast** — Audio a texto (necesita Key gratuita de Groq)
> - 📕 **Xiaohongshu** — Buscar, leer, comentar (escritorio vía OpenCLI; servidor vía xiaohongshu-mcp con QR)
> - 📖 **Reddit** — Buscar y leer posts (requiere login: OpenCLI de escritorio o rdt-cli + Cookie)
> - 📘 **Facebook** — Buscar, páginas, Feed, grupos (escritorio vía OpenCLI, reutiliza login de Chrome)
> - 📷 **Instagram** — Buscar usuarios, perfil, posts recientes, Explore (escritorio vía OpenCLI, reutiliza login de Chrome)
> - 📺 **Bilibili completo** — Popular, ranking, búsqueda, detalle de video (bili-cli, sin login)
> - 💼 **LinkedIn** — Perfil, búsqueda de empleos
>
> Dime cuáles quieres, por ejemplo "Instálame Xiaohongshu y Twitter" o "Instálame Facebook e Instagram". O di "Instala todo".

Según la elección del usuario, ejecuta:

```bash
agent-reach install --env=auto --channels=opencli,xiaohongshu   # Ejemplo: usuario de escritorio eligió XHS (respaldado por OpenCLI)
agent-reach install --env=auto --channels=facebook,instagram    # Ejemplo: usuario de escritorio eligió canales sociales Meta
agent-reach install --env=auto --channels=all              # Usuario quiere todo
```

Nombres de canales soportados: `opencli`, `twitter`, `xiaoyuzhou`, `xueqiu`, `xiaohongshu`, `reddit`, `facebook`, `instagram`, `bilibili`, `linkedin`, `all`

### Paso 3: Arreglar lo que está roto

Ejecuta `agent-reach doctor` y revisa la salida.

Intenta llevar tantos canales como sea posible a ✅. Si algo falló durante la instalación o aparece como ❌/⚠️ en doctor, diagnostica el problema e intenta arreglarlo — pero mantente dentro de los límites anteriores. Si un arreglo requiere permisos elevados o cambios del sistema, pregunta al usuario primero.

Solo pregunta al usuario cuando realmente necesites su input (credenciales, permisos, etc.).

### Paso 3: Configurar lo que necesita input del usuario

Algunos canales necesitan credenciales que solo el usuario puede proveer. Según la salida de doctor, pide lo que falta:

> 🔒 **Consejo de seguridad:** Para plataformas que necesitan cookies o sesiones del navegador (Twitter, Xiaohongshu, Reddit, Facebook, Instagram), recomendamos usar una **cuenta dedicada/secundaria** en lugar de tu cuenta principal. La autenticación por cookie/sesión del navegador implica dos riesgos:
> 1. **Baneo de cuenta** — Las plataformas pueden detectar llamadas a la API que no son de un navegador normal y restringir o banear la cuenta
> 2. **Exposición de credenciales** — Las cookies dan acceso completo a la cuenta; usar una cuenta secundaria limita el impacto si las credenciales se filtran

> 🍪 **Cookie / Login:**
>
> Para plataformas que necesitan Cookie (Twitter, Xueqiu, etc.), **prioriza importar con Cookie-Editor**, es la forma más simple y confiable:
> 1. El usuario inicia sesión en la plataforma desde su navegador
> 2. Instala la extensión [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) de Chrome
> 3. Haz clic en la extensión → Export → Header String
> 4. Pega la cadena exportada al Agent
>
> **Usuarios de PC local** también pueden usar `agent-reach configure --from-browser chrome` para extraer automáticamente (soporta Twitter + Xiaohongshu + Xueqiu). Las plataformas OpenCLI (Reddit, backend de escritorio de Xiaohongshu, Facebook, Instagram) priorizan reutilizar el login de Chrome, no necesitas enviar la Cookie al Agent.

**Búsqueda y publicación en Twitter:**
> "Para desbloquear la búsqueda en Twitter, necesito tus cookies de Twitter. Instala la extensión Cookie-Editor de Chrome, ve a x.com/twitter.com, haz clic en la extensión → Export → Header String, y pégamela."

```bash
agent-reach configure twitter-cookies "CADENA_PEGADA"
```

> **Nota sobre proxy (China continental y otras redes que necesitan VPN):**
>
> twitter-cli y rdt-cli usan Python, en redes que necesitan proxy se puede configurar vía variables de entorno.
>
> **Lo que tú (Agent) necesitas hacer:**
> 1. Confirmar que el usuario configuró proxy: `agent-reach configure proxy http://user:pass@ip:port`
> 2. Configurar variables de entorno: `export HTTP_PROXY="..." HTTPS_PROXY="..."`
> 3. Agent Reach maneja lo demás automáticamente, el usuario no necesita hacer nada extra
>
> Si el usuario reporta "fetch failed", consulta [troubleshooting.md](troubleshooting.md)

**Reddit (el login es obligatorio — sin ruta de cero configuración):**
> Los endpoints anónimos de Reddit están bloqueados, la API oficial requiere aprobación manual. Para usuarios de escritorio, OpenCLI es la primera opción (funciona si has iniciado sesión en reddit.com en el navegador); para servidores/usuarios existentes, usa rdt-cli:

```bash
# PyPI está desactualizado, instalar desde GitHub (misma versión fijada que en _RDT_GIT_SOURCE del código)
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'
rdt login   # Extrae automáticamente la Cookie del navegador; en servidores sin navegador, escribe la Cookie manualmente según las instrucciones de doctor
```

> Acceder a Reddit desde China continental requiere proxy; cuando la IP del servidor es bloqueada, puedes configurar un proxy residencial (como https://webshare.io, ~$1/mes):
> ```bash
> agent-reach configure proxy http://user:pass@ip:port
> ```

**Xiaohongshu / 小红书 (múltiples backends, según entorno):**

> **PC de escritorio (recomendado: OpenCLI):**
> "Xiaohongshu usa OpenCLI — reutiliza tu login del navegador, si has usado Xiaohongshu antes funciona directamente, cero configuración."

```bash
agent-reach install --channels opencli
```

> Después de instalar, guía al usuario en el único paso manual (restricción de seguridad de Chrome, no se puede automatizar):
> 1. Abre https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk
> 2. Haz clic en "Añadir a Chrome"
> 3. Ejecuta `opencli doctor` para verificar (muestra Extension: connected si está conectado)
>
> **Servidor / sin entorno de escritorio (xiaohongshu-mcp):**
> 1. Descarga el binario para tu plataforma desde https://github.com/xpzouying/xiaoyuzhou/releases en `~/.agent-reach/tools/`
> 2. Inicia el servicio (la primera vez descarga ~150MB de navegador headless, ten paciencia)
> 3. Pide al usuario que escanee el código QR para login (el agent llama a `get_login_qrcode` para obtener el QR)
> 4. Conectar: `mcporter config add xiaohongshu http://localhost:18060/mcp`
> 5. Al llamar, siempre usa `--timeout 120000`
>
> **Usuarios existentes (xhs-cli):** Los xhs-cli instalados siguen funcionando como backend alternativo (el upstream dejó de actualizarse en 2026-03, no se recomienda instalar nuevo). `xhs login` extrae automáticamente la Cookie del navegador; si falla, exporta con Cookie-Editor y configura:
> ```bash
> agent-reach configure xhs-cookies "key1=val1; key2=val2; ..."
> ```

**Facebook / Instagram (escritorio OpenCLI):**
> Estas plataformas usan OpenCLI: reutilizan el login de Chrome del usuario, no guardan contraseña ni pasan por la aprobación de la Graph API de Meta. No se recomienda soporte en servidores/sin entorno de escritorio.

```bash
agent-reach install --channels facebook,instagram
```

> Después de instalar:
> 1. Confirma que Chrome tiene la extensión OpenCLI instalada y pasa `opencli doctor`
> 2. Inicia sesión en facebook.com / instagram.com en Chrome
> 3. El Agent llama directamente:
>    ```bash
>    opencli facebook search "query" -f yaml
>    opencli facebook profile zuck -f yaml
>    opencli facebook groups -f yaml
>    opencli instagram search "query" -f yaml     # Búsqueda de usuarios
>    opencli instagram profile nasa -f yaml
>    opencli instagram user nasa -f yaml          # Posts recientes de un usuario
>    ```
>
> Facebook Groups actualmente solo promete leer la lista de grupos y actividad reciente visible tras login, no promete API de posts/comentarios de grupos arbitrarios. La búsqueda de Instagram es de usuarios, no de posts por palabras clave; si muestra 429/error de login, pide al usuario que vuelva a iniciar sesión en Chrome y reduzca la frecuencia.

**Xueqiu / 雪球 (cotizaciones + posts populares):**
> "Xueqiu necesita Cookie de login. Por favor inicia sesión en xueqiu.com en Chrome, luego ejecuta:"

```bash
agent-reach configure --from-browser chrome
```

> La Cookie se extraerá automáticamente junto con otras plataformas.

**Xiaoyuzhou Podcast / 小宇宙播客 (Groq Whisper):**
> "La transcripción de Xiaoyuzhou Podcast ya está instalada, solo necesitas una API Key gratuita de Groq."

El script se instala automáticamente con Agent Reach, el usuario solo necesita proveer la Key:

```bash
agent-reach configure groq-key gsk_xxxxx
```

> **Obtener API Key de Groq (gratis, sin tarjeta de crédito, 30 segundos):**
> 1. Abre https://console.groq.com
> 2. Inicia sesión con tu cuenta de Google/GitHub (o regístrate)
> 3. Menú lateral → API Keys → Create API Key
> 4. Copia la Key (empieza con `gsk_`) y envíasela al Agent
>
> **Forma de uso:**
> El usuario envía un enlace de Xiaoyuzhou al Agent, el Agent llama automáticamente:
> ```bash
> bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh https://www.xiaoyuzhoufm.com/episode/xxxxx
> ```
>
> Descarga audio automáticamente → transcodifica y divide → transcribe con Groq Whisper → genera texto completo en chino.
>
> **Cuota gratuita y limitaciones:**
> - ~2 horas de audio por hora (7200 segundos), después espera 15 minutos para que se recupere automáticamente
> - Para escuchar unos pocos podcasts al día es suficiente
> - Alta calidad de transcripción (Whisper large-v3), pero no distingue hablantes
> - Podcasts de más de 2 horas se recomienda procesar por partes

**LinkedIn (opcional — linkedin-scraper-mcp):**
> "El contenido básico de LinkedIn se puede leer con Jina Reader. La funcionalidad completa (detalle de perfil, búsqueda de empleos) necesita linkedin-scraper-mcp."

```bash
pip install linkedin-scraper-mcp
```

> **Forma de login (necesita interfaz de navegador):**
>
> linkedin-scraper-mcp usa un navegador Chromium para login, necesitas poder ver la ventana del navegador.
>
> **PC de escritorio (con escritorio):** Ejecuta directamente:
> ```bash
> linkedin-scraper-mcp --login --no-headless
> ```
> Se abrirá el navegador, inicia sesión en LinkedIn manualmente.
>
> **Servidor (sin UI):** Necesita operar vía escritorio remoto VNC:
> ```bash
> # 1. Instalar e iniciar VNC en el servidor (si ya tienes, omitir)
> apt install -y tigervnc-standalone-server
> vncserver :1 -geometry 1280x720
>
> # 2. Conectar con un cliente VNC a IP_DEL_SERVIDOR:5901
>
> # 3. En la terminal del escritorio VNC ejecuta:
> export DISPLAY=:1
> linkedin-scraper-mcp --login --no-headless
> ```
> En VNC verás el navegador e iniciarás sesión manualmente. Tras login exitoso, la sesión se guarda en `~/.linkedin-mcp/profile/`.
>
> **Iniciar el servicio MCP después del login:**
> ```bash
> linkedin-scraper-mcp --transport streamable-http --port 8001
> mcporter config add linkedin http://localhost:8001/mcp
> ```
>
> Más detalles en https://github.com/stickerdaniel/linkedin-mcp-server

### Paso 4: Verificación final

Ejecuta `agent-reach doctor` una última vez y reporta los resultados al usuario.

### Paso 5: Configurar monitoreo diario (solo OpenClaw)

Si estás dentro de **OpenClaw**, pregunta al usuario:

> "Agent Reach está instalado. ¿Quieres que configure una tarea diaria de verificación automática? Monitoreará si estos canales están bien y si hay nuevas versiones. Solo te avisa si hay problemas, si todo está normal no te molesta."

Si el usuario acepta, crea un **cron job** (diario, `sessionTarget: "isolated"`, `delivery: "announce"`) con esta tarea:

```
Ejecuta el comando agent-reach watch.
Si la salida contiene "todo normal", no necesitas notificar al usuario, termina silenciosamente.
Si la salida contiene problemas (❌ ⚠️) o nueva versión (🆕), envía el reporte completo al usuario y sugiere soluciones.
Si hay una nueva versión disponible, pregunta al usuario si quiere actualizar (envía esta frase al Agent del usuario para actualizar completamente: Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md).
```

Si el usuario quiere que otro agent lo maneje, deja que elija.

---

## Referencia rápida

| Comando | Qué hace |
|---------|----------|
| `agent-reach install --env=auto` | Instala canales centrales (ligero, cero configuración) |
| `agent-reach install --env=auto --channels=twitter,xiaohongshu` | Instala centrales + opcionales |
| `agent-reach install --env=auto --channels=all` | Instala todo |
| `agent-reach install --env=auto --safe` | Configuración segura (sin cambios automáticos del sistema) |
| `agent-reach install --env=auto --dry-run` | Previsualiza qué se haría |
| `agent-reach doctor` | Muestra estado de canales |
| `agent-reach watch` | Verificación rápida de salud + actualización (para tareas programadas) |
| `agent-reach check-update` | Verificar nuevas versiones |
| `agent-reach configure twitter-cookies "..."` | Desbloquear búsqueda + publicación en Twitter |
| `agent-reach configure proxy URL` | Guardar dirección de proxy (Agent la lee para configurar HTTP_PROXY/HTTPS_PROXY al acceder a Reddit/Twitter u otras redes restringidas, no es un interruptor de desbloqueo automático) |
| `agent-reach configure groq-key gsk_xxx` | Desbloquear transcripción de Xiaoyuzhou Podcast |
| `agent-reach configure fcc-proxy URL` | Configurar proxy de Free Claude Code para transcripción |
| `agent-reach configure kittentts-model MODEL` | Configurar modelo de KittenTTS para texto a voz |
| `agent-reach configure katy-voice VOICE` | Configurar voz de Katy (ej: expr-voice-2-f) |
| `agent-reach configure katy-speed SPEED` | Configurar velocidad de Katy (ej: 1.2) |
| `agent-reach configure katy-4bit true/false` | Activar modo 4-bit para Katy (menos RAM) |

Después de la instalación, usa las herramientas upstream directamente. Consulta SKILL.md para la referencia completa de comandos:

| Plataforma | Herramienta upstream | Ejemplo |
|-----------|---------------------|---------|
| Twitter/X | `twitter` (respaldo `opencli`) | `twitter search "query" -n 10` |
| YouTube | `yt-dlp` | `yt-dlp --dump-json URL` |
| Bilibili | `bili` (subtítulos vía `opencli`) | `bili search "query" --type video` / `opencli bilibili subtitle BVxxx` |
| Reddit | `opencli` (respaldo `rdt`) | `opencli reddit search "query" -f yaml` / `rdt read POST_ID` |
| Facebook | `opencli` | `opencli facebook search "query" -f yaml` |
| Instagram | `opencli` | `opencli instagram user nasa -f yaml` |
| GitHub | `gh` | `gh search repos "query"` |
| Web | `curl` + Jina | `curl -s "https://r.jina.ai/URL"` |
| Búsqueda Exa | `mcporter` | `mcporter call 'exa.web_search_exa(...)'` |
| Xiaohongshu | `opencli` (servidor `mcporter`) | `opencli xiaohongshu search "query" -f yaml` |
| Xiaoyuzhou Podcast | `transcribe.sh` | `bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh <URL>` |
| LinkedIn | `mcporter` | `mcporter call 'linkedin.get_person_profile(...)'` |
| RSS | `feedparser` | `python3 -c "import feedparser; ..."` |
| Transcripción (voz a texto) | `transcribe` | `agent-reach transcribe <audio_file>` |
| Texto a voz | `kittentts` | `agent-reach tts "texto" -o output.wav` |
| Voz a voz (Katy) | `katy` | `agent-reach katy listen audio.wav` / `agent-reach katy speak "texto"` / `agent-reach katy chat` |

> Para plataformas con múltiples backends, usa `agent-reach doctor --json` para ver el `active_backend`.
