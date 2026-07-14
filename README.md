<h1 align="center">👁️ Agent Reach</h1>

> **Fork basado en [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)** — Créditos al creador original. Licencia MIT.

<p align="center">
  <strong>Dale a tu AI Agent capacidades de internet con un solo comando</strong>
</p>

<p align="center">
  La forma más estable de conectarse hoy: elegimos, instalamos y verificamos por ti — las conexiones cambian, tú no te preocupas
</p>

<p align="center">
  <a href="https://trendshift.io/repositories/24387"><img src="https://trendshift.io/api/badge/repositories/24387" alt="Trendshift GitHub Trending #1 Repository of the Day"></a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://github.com/Panniantong/agent-reach/stargazers"><img src="https://img.shields.io/github/stars/Panniantong/agent-reach?style=for-the-badge" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#inicio-rápido">Inicio rápido</a> · <a href="docs/README_en.md">English</a> · <a href="docs/README_ja.md">日本語</a> · <a href="docs/README_ko.md">한국어</a> · <a href="#plataformas-soportadas">Plataformas</a> · <a href="#filosofía-de-diseño">Filosofía</a>
</p>

---

## ¿Por qué necesitas Agent Reach?

Los AI Agents ya pueden escribir código, editar documentos, gestionar proyectos— pero cuando les pides buscar algo en internet, se quedan sin opciones:

- 📺 "Mira qué enseña este tutorial de YouTube" → **No puede**, no obtiene los subtítulos
- 🐦 "Busca qué opinan en Twitter sobre este producto" → **No puede buscar**, la API de Twitter es de pago
- 📖 "Revisa en Reddit si alguien tuvo el mismo bug" → **403 bloqueado**, la IP del servidor es rechazada
- 📕 "Mira las reseñas de este producto en Xiaohongshu" → **No abre**, requiere login para ver
- 📺 "Hay un video técnico en Bilibili, resúmelo" → **No obtiene nada**, las herramientas genéricas están bloqueadas por Bilibili
- 🔍 "Busca comparativas recientes de frameworks LLM" → **No hay buena búsqueda**, o es de pago o mala calidad
- 🌐 "Lee qué dice esta página web" → **Devuelve puro HTML**, ilegible
- 📦 "¿Qué hace este repo de GitHub? ¿Qué dicen los Issues?" → Funciona, pero configurar la autenticación es tedioso
- 📡 "Suscríbete a estos RSS y avísame cuando actualicen" → Tienes que instalar librerías y escribir código

**Todo esto es factible, pero requiere configuración manual**

Cada plataforma tiene su barrera—APIs de pago, bloqueos que esquivar, cuentas para autenticar, datos que limpiar. Tienes que ir uno por uno, instalar herramientas, ajustar configuraciones. Solo para que tu Agent pueda leer Twitter te toma horas.

**Agent Reach lo reduce a una línea:**

```
Instala Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Cópialo para tu Agent, en minutos podrá leer Twitter, buscar en Reddit, ver YouTube, revisar Xiaohongshu.

**¿Ya lo tienes instalado? Actualizar también es una línea:**

```
Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

> ⭐ **Haz Star a este proyecto**, rastrearemos continuamente los cambios en cada plataforma y añadiremos nuevas conexiones. Tú no vigilas—si una plataforma bloquea, lo arreglamos; si hay una nueva conexión, la añadimos.

### ✅ Antes de empezar, quizás quieras saber

| | |
|---|---|
| 💰 **Totalmente gratis** | Todas las herramientas son open source, todas las APIs son gratuitas. Lo único que podría costar es el proxy del servidor (~$1/mes), en tu PC local no |
| 🔒 **Privacidad y seguridad** | Las Cookies se guardan solo en tu máquina, no se suben ni comparten. Código completamente open source, auditable en cualquier momento |
| 🔄 **Actualización continua** | Cada plataforma tiene «preferida + alternativa» con múltiples backends. Si una conexión falla, cambiamos a la siguiente sin que notes nada (ejemplo real 2026-06: yt-dlp fue bloqueado por Bilibili → cambiamos a bili-cli, cero acción del usuario) |
| 🤖 **Compatible con todos los Agents** | Claude Code, OpenClaw, Cursor, Windsurf... cualquier Agent que ejecute comandos de línea puede usarlo |
| 🩺 **Diagnóstico incluido** | `agent-reach doctor` un solo comando te dice qué funciona, qué no, y cómo arreglarlo |

---

## Plataformas soportadas

| Plataforma | Listo para usar | Se desbloquea con configuración | Cómo configurar |
|------------|----------------|-------------------------------|-----------------|
| 🌐 **Web** | Leer cualquier página | — | Sin configuración |
| 📺 **YouTube** | Extracción de subtítulos + búsqueda de videos | — | Sin configuración |
| 📡 **RSS** | Leer cualquier fuente RSS/Atom | — | Sin configuración |
| 🔍 **Búsqueda web** | — | Búsqueda semántica web | Auto-configurado (vía MCP, gratis sin Key) |
| 📦 **GitHub** | Leer repos públicos + búsqueda | Repos privados, crear Issues/PRs, Fork | Di a tu Agent "Ayúdame a login en GitHub" |
| 🐦 **Twitter/X** | Leer un tweet individual | Buscar tweets, navegar timeline, leer hilos | Di a tu Agent "Configura Twitter" |
| 📺 **Bilibili** | Búsqueda + detalles de video (bili-cli, sin login) | Subtítulos (OpenCLI) | Di a tu Agent "Configura Bilibili" |
| 📖 **Reddit** | — (sin ruta de cero configuración: la API anónima está bloqueada) | Buscar + leer posts y comentarios | Instala OpenCLI en escritorio con login del navegador; o rdt-cli + Cookie |
| 📘 **Facebook** | — | Buscar, páginas, Feed, grupos | Instala OpenCLI en escritorio (reutiliza login de Chrome) |
| 📷 **Instagram** | — | Buscar usuarios, perfil, posts recientes, Explore | Instala OpenCLI en escritorio (reutiliza login de Chrome) |
| 📕 **Xiaohongshu** | — | Buscar, leer, comentar | Instala OpenCLI en escritorio (funciona con haber iniciado sesión); en servidor usa xiaohongshu-mcp con código QR |
| 💼 **LinkedIn** | Jina Reader para páginas públicas | Detalle de perfil, página de empresa, búsqueda de empleos | Di a tu Agent "Configura LinkedIn" |
| 💻 **V2EX** | Posts populares, posts por nodo, detalle de post + respuestas, info de usuario | — | Sin configuración |
| 📈 **Xueqiu** | Cotizaciones, buscar acciones, posts populares, ranking de acciones | — | Di a tu Agent "Configura Xueqiu" |
| 🎙️ **Xiaoyuzhou Podcast** | — | Convertir audio a texto (Whisper, Key gratuita) | Di a tu Agent "Configura Xiaoyuzhou" |
| 🔊 **KittenTTS** | — | Texto a voz (modelo local ligero) | Di a tu Agent "Instala KittenTTS" |
| 🗣️ **Katy** | Voz a voz local (Whisper + Qwen2.5 + KittenTTS) | Memoria persistente, alertas proactivas | Di a tu Agent "Configura Katy" |

> **¿No sabes cómo configurar? No busques en la documentación.** Simplemente di a tu Agent "Configura XXX", él sabrá qué necesita y te guiará paso a paso.
>
> 🍪 Las plataformas que requieren Cookie/login (Twitter, Xiaohongshu, Reddit, Facebook, Instagram, etc.) priorizan que el usuario inicie sesión en su propio navegador. OpenCLI reutiliza el login de Chrome; los CLIs tradicionales necesitan exportar Cookie con Cookie-Editor.
>
> 🔒 Las Cookies se guardan solo en tu máquina, no se suben ni comparten. Código completamente open source.
> 💻 En tu PC local no necesitas proxy. El proxy solo se necesita en servidores (~$1/mes).

---

## Inicio rápido

> ⚠️ **Usuarios de OpenClaw: asegúrense de tener habilitados los permisos de exec**
>
> Agent Reach depende de que el Agent ejecute comandos de shell (`pip install`, `mcporter`, `twitter`, etc.). Si tu OpenClaw usa la configuración de herramientas `messaging` por defecto, el Agent no podrá ejecutar comandos. **Antes de instalar, habilita los permisos de exec**:
>
> ```bash
> openclaw config set tools.profile "coding"
> ```
> O configura en `~/.openclaw/openclaw.json`: `"tools": { "profile": "coding" }`.
> Después reinicia el Gateway (`openclaw gateway restart`) y abre una nueva conversación. Otras plataformas (Claude Code, Cursor, Windsurf, etc.) no tienen esta restricción.

Copia esta línea para tu AI Agent (Claude Code, OpenClaw, Cursor, etc.):

```
Instala Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Solo eso. El Agent se encargará de todo lo demás.

> 🔄 **¿Ya lo tienes instalado?** Actualizar también es una línea:
> ```
> Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
> ```

> 🛡️ **¿Preocupado por la seguridad?** Puedes usar el modo seguro—no instala paquetes del sistema automáticamente, solo te dice qué necesitas:
> ```
> Instala Agent Reach (modo seguro): https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> Usa el parámetro --safe al instalar
> ```

<details>
<summary>¿Qué hace? (clic para expandir)</summary>

1. **Instala la CLI** — `pip install` instala `agent-reach` (incluye yt-dlp, feedparser)
2. **Instala infraestructura del sistema** — Detecta e instala Node.js, gh CLI, mcporter automáticamente
3. **Configura el motor de búsqueda** — Conecta Exa vía MCP (gratis, sin API Key)
4. **Detecta el entorno** — Determina si es PC local o servidor, da recomendaciones de configuración correspondientes
5. **Registra SKILL.md** — Instala la guía de uso en el directorio de skills del Agent, para que automáticamente sepa qué herramienta usar cuando necesite "investigar en la web", "buscar en Twitter", "ver videos", etc.
6. **Te pregunta si quieres más** — Por defecto solo activa 6 canales de cero configuración; para Xiaohongshu, Twitter, Reddit, Facebook, Instagram que requieren login, el Agent muestra un menú y solo instala los que elijas

Después de instalar, `agent-reach doctor` un solo comando te dice el estado de cada canal y por qué ruta está funcionando.
</details>

---

## Listo para usar

Sin necesidad de configuración, solo dile a tu Agent:

- "Lee este enlace" → `curl https://r.jina.ai/URL` lee cualquier página web
- "¿Qué hace este repo de GitHub?" → `gh repo view owner/repo`
- "¿Qué dice este video de YouTube?" → `yt-dlp` extrae subtítulos
- "Busca tutoriales de IA en Bilibili" → `bili search` (sin login)
- "Busca comparativas de frameworks LLM" → Búsqueda semántica Exa
- "Suscríbete a este RSS" → `feedparser` para parsear

**No necesitas memorizar comandos.** Después de leer SKILL.md, el Agent sabe qué ejecutar. Para plataformas que requieren login (Xiaohongshu, Twitter, Reddit, Facebook, Instagram), di "Configura XXX" para desbloquearlas.

---

## Límites de capacidad: leer contenido vs operar web

Algunas tareas van más allá de "leer": operaciones web con login, envío de formularios, aislamiento de múltiples cuentas, sesiones de navegador paralelas, verificación, captchas, etc. Para estos escenarios de "acción manual", puedes complementar con herramientas de automatización de navegador como [BrowserAct](https://www.browseract.ai/Agent)—más de 30 habilidades preconfiguradas para plataformas, compatible con Claude Code / OpenClaw / Cursor y otros Agents principales.

---

## 🗣️ Katy — Asistente de Voz Local

Katy es un asistente de voz que funciona **100% local** sin API keys. Usa Whisper para escuchar, Qwen2.5 para pensar, y KittenTTS para responder con voz femenina en español.

```bash
# Instalar dependencias
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers kittentts openai-whisper
choco install espeak-ng

# Configurar Katy
agent-reach configure katy-voice expr-voice-2-f   # Voz femenina
agent-reach configure katy-speed 1.2              # Velocidad

# Usar Katy
agent-reach katy listen audio.wav    # Entender audio
agent-reach katy speak "Hola"        # Generar voz
agent-reach katy chat                # Chat interactivo
agent-reach katy continuous          # Escucha continua con wake word
agent-reach katy alerts              # Alertas proactivas (clima, sismos)
agent-reach katy vault --status      # Memoria persistente
```

| Característica | Detalle |
|----------------|---------|
| **STT (escuchar)** | Whisper small — modelo de OpenAI, funciona en CPU |
| **LLM (pensar)** | Qwen2.5-0.5B — modelo local (~1GB RAM), responde en español |
| **TTS (hablar)** | KittenTTS — modelo local ligero (22MB), voz femenina |
| **Memoria** | obsidian-mind vault — persistencia entre sesiones |
| **Alertas** | Clima (wttr.in) + Sismos (USGS) — gratis sin API keys |
| **Archivos** | Temporales — se borran después de usar |
| **Requisitos** | ~2GB RAM, funciona sin GPU |

---

## Filosofía de diseño

**Agent Reach es una capa de capacidades (capability layer), no otra herramienta.**

Está un nivel por encima de cualquier implementación específica—se encarga de **selección, instalación, verificación y enrutamiento**, no de la lectura en sí. La lectura la hace el Agent llamando directamente a las herramientas upstream, sin capa de envoltura.

Cuando preparas el entorno para un nuevo Agent, siempre pierdes tiempo buscando herramientas, instalando dependencias, ajustando configuración—¿Qué uso para Twitter? ¿Cómo me登录 en Reddit? ¿El CLI de Xiaohongshu dejó de actualizarse, qué uso ahora? Cada vez hay que empezar de cero. Agent Reach hace algo simple: **la conexión más estable de hoy, la elegimos, instalamos y verificamos por ti. Las conexiones cambian (en marzo 2026 un grupo de CLIs individuales dejaron de actualizarse, cambiamos la ruta), tú no te preocupas.**

### 🔌 Cada plataforma = lista ordenada de preferida + alternativas

Cambiar la conexión = reordenar la lista, no reescribir código. `agent-reach doctor` te dice qué backend está usando cada plataforma **ahora mismo**.

```
channels/
├── web.py          → Jina Reader
├── twitter.py      → twitter-cli ▸ OpenCLI ▸ bird
├── youtube.py      → yt-dlp
├── github.py       → gh CLI
├── bilibili.py     → bili-cli ▸ OpenCLI ▸ API de búsqueda (yt-dlp fue bloqueado por Bilibili, retirado)
├── reddit.py       → OpenCLI ▸ rdt-cli (sin ruta de cero configuración, requiere login)
├── facebook.py     → OpenCLI (login del navegador de escritorio)
├── instagram.py    → OpenCLI (login del navegador de escritorio)
├── xiaohongshu.py  → OpenCLI ▸ xiaohongshu-mcp ▸ xhs-cli
├── linkedin.py     → linkedin-mcp ▸ Jina Reader
├── rss.py          → feedparser
├── exa_search.py   → Exa vía mcporter
├── kittentts.py    → KittenTTS (texto a voz)
├── katy.py         → Whisper (escuchar) + Qwen2.5 (pensar) + KittenTTS (hablar)
├── __init__.py     → Registro de canales (para diagnóstico de doctor)

katy_*.py           → Módulos de Katy (memoria, alertas, listener, LLM)
```

Cada archivo de canal **prueba real** cada backend candidato en orden (no solo verifica si el comando existe), el primero que funciona completamente es seleccionado; los que fallan dan instrucciones de reparación. La lectura y búsqueda reales las hace el Agent llamando directamente a las herramientas upstream.

### Selección actual

| Escenario | Preferida | Alternativa | Por qué |
|-----------|-----------|-------------|---------|
| Leer web | [Jina Reader](https://github.com/jina-ai/reader) | — | Gratis, sin API Key |
| Leer Twitter | [twitter-cli](https://github.com/public-clis/twitter-cli) | [OpenCLI](https://github.com/jackwener/opencli) | Estable en pruebas; OpenCLI como respaldo con login del navegador |
| Reddit | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | [rdt-cli](https://github.com/public-clis/rdt-cli) | API anónima bloqueada, API oficial con aprobación—solo queda login |
| Facebook | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | — | Graph API/Groups API restringidas; login del navegador es lo más práctico |
| Instagram | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | Graph API oficial (Business/Creator + aprobación) | instaloader inestable; OpenCLI reutiliza sesiones reales del navegador |
| Subtítulos YouTube + búsqueda | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | — | 154K Star, YouTube sigue siendo lo mejor (nota: ya no se usa para Bilibili) |
| Bilibili | [bili-cli](https://github.com/public-clis/bili-cli) | OpenCLI ▸ API de búsqueda | yt-dlp bloqueado por Bilibili 412 (prueba real 2026-06), bili-cli busca y lee sin login |
| Búsqueda web | [Exa](https://exa.ai) vía [mcporter](https://github.com/nicobailon/mcporter) | — | Búsqueda semántica AI, MCP sin Key |
| GitHub | [gh CLI](https://cli.github.com) | — | Herramienta oficial, API completa tras autenticación |
| Leer RSS | [feedparser](https://github.com/kurtmckee/feedparser) | — | Estándar del ecosistema Python |
| Xiaohongshu | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (servidor) ▸ xhs-cli | El autor de xhs-cli migró a OpenCLI (24K Star); login del navegador sin fricción |
| LinkedIn | [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) | Jina Reader | Servicio MCP, automatización de navegador |
| Voz a texto | [Free Claude Code](https://github.com/Panniantong/free-claude-code) proxy | Groq ▸ OpenAI | FCC proxy inferencia local gratis, sin API Key |
| Texto a voz | [KittenTTS](https://github.com/KittenML/KittenTTS) | — | Modelo local ligero (0.6B), sin GPU |
| Voz a voz (Katy) | [Whisper](https://github.com/openai/whisper) + [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) + KittenTTS | — | STT + LLM + TTS local, sin API Key, memoria persistente |

> 📌 Estas son las «selecciones actuales», basadas en pruebas reales periódicas. Si una ruta falla, cambiamos a la siguiente—`agent-reach doctor` siempre te dice cuál se está usando.

---

## Seguridad

Agent Reach está diseñado con seguridad como prioridad:

| Medida | Descripción |
|--------|-------------|
| 🔒 **Almacenamiento local de credenciales** | Cookies y Tokens se guardan solo en `~/.agent-reach/config.yaml`, permisos 600 (solo el propietario puede leer/escribir), no se suben ni comparten |
| 🛡️ **Modo seguro** | `agent-reach install --safe` no modifica el sistema automáticamente, solo lista qué necesitas, tú decides si instalar |
| 👀 **Totalmente open source** | Código transparente, auditable en cualquier momento. Todas las dependencias también son open source |
| 🔍 **Dry Run** | `agent-reach install --dry-run` previsualiza todas las operaciones sin hacer cambios |
| 🧩 **Arquitectura extraíble** | ¿No confías en algún componente? Cambia el archivo del canal correspondiente, no afecta a los demás |

### 🍪 Recomendaciones de seguridad con Cookies

> ⚠️ **Riesgo de baneo:** Usar Cookies para autenticarse en plataformas (Twitter, Xiaohongshu, etc.) implica **riesgo de ser detectado y baneado por la plataforma**. Usa **cuentas secundarias dedicadas**, nunca tu cuenta principal.

Las plataformas que requieren Cookie o login (Twitter, Xiaohongshu, Reddit, Facebook, Instagram, etc.) recomiendan usar **cuentas secundarias dedicadas**. Dos razones:
1. **Riesgo de baneo** — La plataforma puede detectar llamadas a la API que no son de un navegador normal, resultando en restricción o baneo de la cuenta
2. **Riesgo de seguridad** — Una Cookie equivale a acceso completo; usar una cuenta secundaria limita el impacto si las credenciales se filtran

### 📦 Métodos de instalación

| Método | Comando | Ideal para |
|--------|---------|-----------|
| Totalmente automático (por defecto) | `agent-reach install --env=auto` | PC personal, entorno de desarrollo |
| Modo seguro | `agent-reach install --env=auto --safe` | Servidores de producción, máquinas compartidas |
| Solo previsualizar | `agent-reach install --env=auto --dry-run` | Ver qué haría antes de ejecutar |

### 🗑️ Desinstalar

```bash
agent-reach uninstall
```

Limpia: `~/.agent-reach/` (incluye todos los tokens/cookies), archivos skill de cada Agent, configuración MCP en mcporter.

```bash
# Solo previsualizar, no borrar realmente
agent-reach uninstall --dry-run

# Solo borrar archivos skill, mantener configuración de tokens (para reinstalar)
agent-reach uninstall --keep-config
```

Desinstalar el paquete Python: `pip uninstall agent-reach`

---

## ⭐ Por qué merece un Star

Uso este proyecto todos los días, así que lo mantendré continuamente.

- Si hay nuevas necesidades o solicitan plataformas, las iré añadiendo
- Cada canal Intentaré que sea **usable, cómodo y gratuito**
- Si una plataforma cambia su anti-scraping o su API, encontraré la solución

Contribuyendo a la infraestructura de Web 4.0.

Star ahora, para que lo encuentres cuando lo necesites. ⭐

---

## Agradecimientos

[OpenCLI](https://github.com/jackwener/opencli) · [twitter-cli](https://github.com/public-clis/twitter-cli) · [rdt-cli](https://github.com/public-clis/rdt-cli) · [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) · [xhs-cli](https://github.com/jackwener/xiaohongshu-cli) · [bili-cli](https://github.com/public-clis/bilibili-cli) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Jina Reader](https://github.com/jina-ai/reader) · [Exa](https://exa.ai) · [mcporter](https://github.com/nicobailon/mcporter) · [feedparser](https://github.com/kurtmckee/feedparser) · [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) · [KittenTTS](https://github.com/KittenML/KittenTTS) · [Whisper](https://github.com/openai/whisper) · [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) · [obsidian-mind](https://github.com/breferrari/obsidian-mind) · [Free Claude Code](https://github.com/Panniantong/free-claude-code)

## Contacto

- 📧 **Email:** pnt01@foxmail.com
- 🐦 **Twitter/X:** [@Neo_Reidlab](https://x.com/Neo_Reidlab)

### Compilando prácticas reales de AI Agents

Estoy recopilando recientemente prácticas, problemas y oportunidades de AI Agents / AI workflows en escenarios reales.

Agent Reach es mi propio intento open source: permitir que los Agents lean la internet de forma más sencilla, hagan research, monitoreo de mercado, recolección de datos, y por eso me he encontrado con muchos escenarios interesantes.

Si también estás explorando direcciones similares, bienvenido a contactarme:

- Has encontrado problemas concretos de obtención de información, búsqueda, monitoreo, análisis o automatización en tu negocio
- Estás intentando usar Agents para transformar flujos de marketing, ventas, operaciones, inversión, contenido, datos
- Estás haciendo AI Agents, automatización de navegadores, recolección de datos, herramientas verticales o productos relacionados
- Tienes observaciones, casos o dudas sobre cómo los Agents se implementan en la práctica

Al agregar como amigo, por favor pon: `AI Agent + tu área de interés`.

Priorizaré responder a quienes tengan escenarios claros o preguntas concretas. Si es apropiado, también te invitaré a grupos de intercambio.

<p align="center">
  <img src="docs/wechat-group-qr.jpg" width="280" alt="WeChat QR">
</p>

> Para reportar bugs y solicitar funcionalidades usa [GitHub Issues](https://github.com/Panniantong/Agent-Reach/issues), es más fácil de rastrear.

## Licencia

[MIT](LICENSE)

## Enlaces de interés

[方舟 Agent Plan Suscripción de modelos](https://dis.chatdesks.cn/chatdesk/hsyqAgent-Reach.html) — Integra modelos SOTA desarrollados por ByteDance incluyendo Doubao-Seed, Doubao-Seedance, Doubao-Seedream, cubriendo tareas de texto, código, imagen, video y multimodal. Soporta los últimos MiniMax-M3, DeepSeek-V4, GLM-5.2, Doubao-Seed-2.0, Kimi-K2.6 y más, sin límite de herramientas. Suscripción única para cambiar entre motores AI según la tarea.

[Tencent Cloud OpenClaw](https://www.tencentcloud.com/act/pro/intl-openclaw?referral_code=G76Y819A&lang=zh&pg=) — Despliega OpenClaw en Tencent Cloud Lighthouse en segundos, conecta Agent Reach mediante对话 y dale a tu OpenClaw capacidades de internet con un clic.

[Mirror AtomGit](https://atomgit.com/qq_51337814/Agent-Reach) — Mirror sincronizado de Agent Reach en AtomGit, para fácil acceso y clonación desde China.

## Historial de Stars

[![Star History Chart](https://api.star-history.com/svg?repos=Panniantong/Agent-Reach&type=Date&v=20260309)](https://star-history.com/#Panniantong/Agent-Reach&Date)
