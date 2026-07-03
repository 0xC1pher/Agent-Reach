<h1 align="center">👁️ Agent Reach</h1>

<p align="center">
  <strong>Dale a tu AI Agent capacidades de internet con un solo comando</strong>
</p>

<p align="center">
  La ruta de acceso más confiable para cada plataforma — elegida, instalada y verificada por ti. Los backends van y vienen; tú no te enteras.
</p>

<p align="center">
  <a href="https://trendshift.io/repositories/24387"><img src="https://trendshift.io/api/badge/repositories/24387" alt="Trendshift GitHub Trending #1 Repository of the Day"></a>
</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://github.com/Panniantong/agent-reach/stargazers"><img src="https://img.shields.io/github/stars/Panniantong/agent-reach?style=for-the-badge" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#inicio-rápido">Inicio rápido</a> · <a href="../README.md">中文</a> · <a href="README_ja.md">日本語</a> · <a href="README_ko.md">한국어</a> · <a href="#plataformas-soportadas">Plataformas</a> · <a href="#filosofía-de-diseño">Filosofía</a>
</p>

> **Sin token ni afiliación crypto:** Agent Reach no tiene token oficial, moneda, producto de inversión, programa de comisiones, conexión de billetera, ni proyecto en Solana/Pump.fun. Cualquier proyecto crypto que use el nombre Agent Reach, la URL de GitHub o la identidad del autor NO está afiliado a este repositorio. No conectes una billetera ni reclames comisiones basado en mensajes, posts o links que digan lo contrario.

---

## ¿Por qué Agent Reach?

Los AI Agents ya pueden acceder a internet — pero "poder ir online" es apenas el comienzo.

La información más valiosa vive en plataformas sociales y nicho: discusiones en Twitter, opiniones en Reddit, tutoriales de YouTube, reseñas en Xiaohongshu, videos de Bilibili, actividad en GitHub… **Ahí es donde la densidad de información es más alta**, pero cada plataforma tiene sus barreras:

| Dolor | Realidad |
|-------|----------|
| API de Twitter | Pago por uso, uso moderado ~$215/mes |
| Reddit | IPs de servidor reciben 403 |
| Xiaohongshu | Requiere login para navegar |
| Bilibili | Bloquea IPs de ultramar/servidor |

Para conectar tu Agent a estas plataformas, tendrías que buscar herramientas, instalar dependencias y depurar configuraciones — una por una.

**Agent Reach reduce esto a un solo comando:**

```
Instala Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Cópialo para tu Agent. En minutos podrá leer tweets, buscar en Reddit y ver Bilibili.

**¿Ya lo tienes instalado? Actualizar también es un comando:**

```
Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

### ✅ Antes de empezar, quizás quieras saber

| | |
|---|---|
| 💰 **Totalmente gratis** | Todas las herramientas son open source, todas las APIs son gratuitas. Lo único que podría costar es el proxy del servidor (~$1/mes) — en tu PC local no necesitas uno |
| 🔒 **Privacidad segura** | Las Cookies se quedan en tu máquina. Nunca se suben. Código completamente open source — auditable en cualquier momento |
| 🔄 **Se mantiene actualizado** | Cada plataforma usa una lista de backends preferida + alternativa. Cuando una ruta de acceso muere, cambiamos a la siguiente — tú no lo notas (junio 2026: Bilibili bloqueó yt-dlp con 412 → cambiamos a bili-cli, cero acción de tu parte) |
| 🤖 **Funciona con cualquier Agent** | Claude Code, OpenClaw, Cursor, Windsurf… cualquier Agent que ejecute comandos |
| 🩺 **Diagnóstico incluido** | `agent-reach doctor` — un solo comando muestra qué funciona, qué no, y cómo arreglarlo |

---

## Plataformas soportadas

| Plataforma | Capacidades | Configuración | Notas |
|------------|------------|:-------------:|-------|
| 🌐 **Web** | Leer | Cero config | Cualquier URL → Markdown limpio ([Jina Reader](https://github.com/jina-ai/reader) ⭐9.8K) |
| 🐦 **Twitter/X** | Leer · Buscar | Cookie | Cookie desbloquea búsqueda, timeline, lectura de tweets, artículos ([twitter-cli](https://github.com/public-clis/twitter-cli)) |
| 📕 **Xiaohongshu** | Leer · Buscar · Comentar | OpenCLI / MCP | Escritorio: [OpenCLI](https://github.com/jackwener/opencli) (reutiliza sesión del navegador); Servidor: [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (login con QR); xhs-cli legacy aún funciona |
| 📘 **Facebook** | Buscar · Perfiles · Feed · Lista de grupos | OpenCLI | Solo escritorio: [OpenCLI](https://github.com/jackwener/opencli) reutiliza tu sesión iniciada en Chrome |
| 📷 **Instagram** | Buscar usuarios · Perfiles · Posts recientes · Explore | OpenCLI | Solo escritorio: [OpenCLI](https://github.com/jackwener/opencli) reutiliza tu sesión iniciada en Chrome |
| 💼 **LinkedIn** | Jina Reader (páginas públicas) | Perfiles completos, empresas, búsqueda de empleos | Di a tu Agent "Configura LinkedIn" |
| 💻 **V2EX** | Posts populares · Posts por nodo · Detalle + respuestas · Perfil de usuario | Cero config | API JSON pública, sin autenticación. Ideal para contenido tech |
| 📈 **Xueqiu (雪球)** | Cotizaciones · Buscar · Posts populares · Acciones populares | Cookie del navegador | Di a tu Agent "Configura Xueqiu" |
| 🎙️ **Xiaoyuzhou Podcast** | Transcripción | API Key gratuita | Audio de podcast → texto completo vía Groq Whisper (gratis) |
| 🔍 **Búsqueda web** | Buscar | Auto-configurado | Se configura durante la instalación, gratis, sin API Key ([Exa](https://exa.ai) vía [mcporter](https://github.com/nicepkg/mcporter)) |
| 📦 **GitHub** | Leer · Buscar | Cero config | Potenciado por [gh CLI](https://cli.github.com). Repos públicos funcionan inmediatamente. `gh auth login` desbloquea Fork, Issue, PR |
| 📺 **YouTube** | Leer · **Buscar** | Cero config | Subtítulos + búsqueda en 1800+ sitios de video ([yt-dlp](https://github.com/yt-dlp/yt-dlp) ⭐148K) |
| 📺 **Bilibili** | Leer · **Buscar** | Cero config | Búsqueda + detalle de video vía [bili-cli](https://github.com/public-clis/bili-cli) (sin login); subtítulos vía [OpenCLI](https://github.com/jackwener/opencli). yt-dlp está bloqueado por Bilibili y ya no se usa aquí |
| 📡 **RSS** | Leer | Cero config | Cualquier fuente RSS/Atom ([feedparser](https://github.com/kurtmckee/feedparser) ⭐2.3K) |
| 📖 **Reddit** | Buscar · Leer | OpenCLI / Cookie | Sin ruta de cero configuración (endpoints anónimos bloqueados). Escritorio: [OpenCLI](https://github.com/jackwener/opencli) vía sesión del navegador; o [rdt-cli](https://github.com/public-clis/rdt-cli) + cookie |

> **Niveles de configuración:** Cero config = instalar y listo · Auto-configurado = se maneja durante la instalación · mcporter = necesita servicio MCP · Cookie = exportar del navegador · Proxy = $1/mes

---

## Inicio rápido

> ⚠️ **Usuarios de OpenClaw: habilita el permiso `exec` primero**
>
> Agent Reach depende de que el Agent ejecute comandos de shell (`pip install`, `mcporter`, `twitter`, etc.). Si tu OpenClaw usa el perfil de herramientas `messaging` por defecto, el Agent no podrá ejecutarlos. **Habilita `exec` antes de instalar:**
>
> ```bash
> openclaw config set tools.profile "coding"
> ```
> O configura `"tools": { "profile": "coding" }` en `~/.openclaw/openclaw.json`. Después de cambiarlo, reinicia el Gateway (`openclaw gateway restart`) y abre una nueva conversación. Otras plataformas (Claude Code, Cursor, Windsurf, etc.) no se ven afectadas.

Copia esto para tu AI Agent (Claude Code, OpenClaw, Cursor, etc.):

```
Instala Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

El Agent se instala automáticamente, detecta tu entorno y te dice qué está listo.

> 🔄 **¿Ya lo tienes instalado?** Actualizar es un comando:
> ```
> Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
> ```

> 🛡️ **¿Preocupado por la seguridad?** Usa el modo seguro — no instala paquetes del sistema automáticamente, solo te dice qué necesitas:
> ```
> Instala Agent Reach (modo seguro): https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> Usa el parámetro --safe al instalar
> ```

<details>
<summary>Instalación manual</summary>

```bash
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```
</details>

<details>
<summary>Instalar como Skill (Claude Code / OpenClaw / cualquier agent con soporte de Skills)</summary>

```bash
npx skills add Panniantong/Agent-Reach@agent-reach
```

Después de instalar el Skill, el Agent detectará automáticamente si la CLI `agent-reach` está disponible y la instalará si es necesario.

> Si instalas vía `agent-reach install`, el skill se registra automáticamente — no necesitas pasos extra.
>
> ¿Prefieres un archivo skill solo en inglés? Configura un locale en inglés o exporta `AGENT_REACH_LANG=en`
> antes de ejecutar `agent-reach install --env=auto` o `agent-reach skill --install`.
> El archivo instalado siempre se escribe como `SKILL.md`, así que cambiar de idioma significa reejecutar
> el comando de instalación con el nuevo locale y reemplazar el archivo skill previamente instalado.
</details>

---

## Listo para usar

Sin necesidad de configuración, solo dile a tu Agent:

- "Lee este enlace" → `curl https://r.jina.ai/URL` para cualquier página web
- "¿Qué hace este repo de GitHub?" → `gh repo view owner/repo`
- "¿Qué dice este video?" → `yt-dlp --dump-json URL` para subtítulos
- "Lee este tweet" → `twitter tweet URL`
- "Suscríbete a este RSS" → `feedparser` para parsear feeds
- "Busca frameworks LLM en GitHub" → `gh search repos "LLM framework"`

**No necesitas memorizar comandos.** El Agent lee SKILL.md y sabe qué ejecutar.

---

## Límites de capacidad: leer contenido vs operar páginas web

Algunas tareas van más allá de "leer": operar páginas web con sesión iniciada, enviar formularios, aislar múltiples cuentas, ejecutar sesiones de navegador paralelas, o entregar pasos de alta fricción en flujos de automatización como login, verificación y prompts de control de riesgo. Para estas acciones "manuales" de navegador, Agent Reach se puede combinar con herramientas de automatización como [BrowserAct](https://www.browseract.ai/Agent) — más de 30 habilidades preconfiguradas para plataformas, compatible con Agents principales como Claude Code, OpenClaw y Cursor.

---

## Desbloqueo bajo demanda

¿No lo usas? No lo configures. Cada paso es opcional.

### 🍪 Cookies — Gratis, 2 minutos

Di a tu Agent "Ayúdame a configurar las cookies de Twitter" — te guiará para exportarlas desde tu navegador. En PC local se pueden importar automáticamente.

### 🌐 Proxy — $1/mes, solo en redes restringidas

La mayoría de usuarios no necesitan proxy. Si tu red bloquea Reddit/Twitter (ej. China continental) consigue uno ([Webshare](https://webshare.io) recomendado, $1/mes) y envía la dirección a tu Agent — la guarda y exporta HTTP(S)_PROXY al llamar a esas herramientas.

> Reddit necesita sesión iniciada de todas formas — OpenCLI usa tu sesión del navegador, o rdt-cli después de `rdt login`. Bilibili funciona vía bili-cli sin proxy.

---

## Estado a un vistazo

```
$ agent-reach doctor

👁️  Agent Reach Status
========================================

✅ Listo para usar:
  ✅ Repos y código de GitHub — repos públicos legibles y buscables
  ✅ Tweets de Twitter/X — legibles. Cookie desbloquea búsqueda y publicación
  ✅ Subtítulos de videos de YouTube — yt-dlp
  ✅ Búsqueda y detalle de videos de Bilibili — bili-cli (subtítulos vía OpenCLI)
  ✅ Fuentes RSS/Atom — feedparser
  ✅ Páginas web (cualquier URL) — API de Jina Reader

🔍 Búsqueda (Key gratuita de Exa para desbloquear):
  ⬜ Búsqueda semántica web — regístrate en exa.ai para key gratuita

🔧 Configurable:
  ⬜ Posts y comentarios de Reddit — necesita login: rdt-cli después de `rdt login`, o sesión del navegador con OpenCLI
  ⬜ Notas de Xiaohongshu — escritorio: OpenCLI (sesión del navegador); servidor: xiaohongshu-mcp (QR)
  ⬜ Facebook / Instagram — escritorio: sesión del navegador con OpenCLI

Estado: 6/9 canales disponibles
```

---

## Filosofía de diseño

**Agent Reach es una capa de capacidades, no otra herramienta.**

Está un nivel por encima de cualquier implementación específica — maneja **selección, instalación, verificación de salud y enrutamiento**, no la lectura en sí. La lectura la hace tu Agent llamando a las herramientas upstream directamente; no hay capa de envoltura.

Cada vez que preparas un nuevo Agent, pierdes tiempo buscando herramientas, instalando dependencias y depurando configuraciones — ¿Qué lee Twitter? ¿Cómo me登录 en Reddit? ¿Qué reemplaza al CLI de Xiaohongshu que fue descontinuado? Cada vez, repites el mismo trabajo. Agent Reach hace una cosa simple: **la ruta de acceso más confiable para cada plataforma, elegida, instalada y verificada por ti. Las rutas de acceso van y vienen (en marzo 2026 un grupo de CLIs de plataforma única dejaron de mantenerse — reenrutamos), para que tú no tengas que preocuparte.**

### 🔌 Cada plataforma = lista ordenada de backends (preferido + alternativas)

Cambiar rutas de acceso significa reordenar la lista, no reescribir código. `agent-reach doctor` te dice **qué backend está usando cada plataforma ahora mismo**.

```
channels/
├── web.py          → Jina Reader
├── twitter.py      → twitter-cli ▸ OpenCLI ▸ bird
├── youtube.py      → yt-dlp
├── github.py       → gh CLI
├── bilibili.py     → bili-cli ▸ OpenCLI ▸ API de búsqueda (yt-dlp retirado, bloqueado con 412)
├── reddit.py       → OpenCLI ▸ rdt-cli (sin ruta de cero configuración, requiere login)
├── facebook.py     → OpenCLI (sesión del navegador de escritorio)
├── instagram.py    → OpenCLI (sesión del navegador de escritorio)
├── xiaohongshu.py  → OpenCLI ▸ xiaohongshu-mcp ▸ xhs-cli
├── linkedin.py     → linkedin-mcp ▸ Jina Reader
├── rss.py          → feedparser
├── exa_search.py   → Exa vía mcporter
├── kittentts.py    → KittenTTS (texto a voz)
└── __init__.py     → Registro de canales (para diagnóstico de doctor)
```

Cada archivo de canal **prueba realmente** sus backends candidatos en orden (no solo verifica que un comando exista) — el primero que funciona completamente se convierte en el backend activo, y los que fallan vienen con instrucciones de reparación. La lectura y búsqueda reales las hace el Agent llamando a las herramientas upstream directamente.

### Selección actual

| Escenario | Preferido | Alternativa | Por qué |
|-----------|-----------|-------------|---------|
| Leer páginas web | [Jina Reader](https://github.com/jina-ai/reader) | — | Gratis, sin API Key |
| Leer tweets | [twitter-cli](https://github.com/public-clis/twitter-cli) | [OpenCLI](https://github.com/jackwener/opencli) | Búsqueda confiable en pruebas reales; OpenCLI como respaldo con sesión del navegador |
| Reddit | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | [rdt-cli](https://github.com/public-clis/rdt-cli) | Endpoints anónimos bloqueados, API oficial con aprobación — solo quedan sesiones con login |
| Facebook | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | — | Acceso a Graph/Groups API muy restringido; sesiones del navegador son lo más práctico |
| Instagram | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | Graph API oficial (Business/Creator + revisión) | Rutas tipo instaloader inestables; OpenCLI reutiliza la sesión real del navegador |
| Subtítulos YouTube + búsqueda | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | — | 154K estrellas, sigue siendo lo mejor para YouTube (ya no se usa para Bilibili) |
| Bilibili | [bili-cli](https://github.com/public-clis/bilibili-cli) | OpenCLI ▸ API de búsqueda | yt-dlp bloqueado por Bilibili con 412 (verificado junio 2026); bili-cli busca y lee sin login |
| Buscar en la web | [Exa](https://exa.ai) vía [mcporter](https://github.com/nicobailon/mcporter) | — | Búsqueda semántica AI, integración MCP, sin API Key |
| GitHub | [gh CLI](https://cli.github.com) | — | Herramienta oficial, API completa tras autenticación |
| Leer RSS | [feedparser](https://github.com/kurtmckee/feedparser) | — | Estándar del ecosistema Python |
| Xiaohongshu | [OpenCLI](https://github.com/jackwener/opencli) (escritorio) | [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (servidor) ▸ xhs-cli | El autor de xhs-cli migró a OpenCLI (24K estrellas); sesiones del navegador sin fricción |
| LinkedIn | [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) | Jina Reader | Servidor MCP, automatización de navegador |
| Voz a texto | [Free Claude Code](https://github.com/Panniantong/free-claude-code) proxy | Groq ▸ OpenAI | FCC proxy inferencia local gratis, sin API Key |
| Texto a voz | [KittenTTS](https://github.com/KittenML/KittenTTS) | — | Modelo local ligero (0.6B), sin GPU |
| Xiaoyuzhou Podcast | `transcribe.sh` | — | `bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh <URL>` |

> 📌 Estas son las selecciones *actuales*, re-verificadas regularmente en máquinas reales. Cuando una ruta muere, cambiamos a la siguiente — `agent-reach doctor` siempre te dice cuál está activa.

---

## Agradecimientos

[twitter-cli](https://github.com/public-clis/twitter-cli) · [rdt-cli](https://github.com/public-clis/rdt-cli) · [xhs-cli](https://github.com/jackwener/xiaohongshu-cli) · [bili-cli](https://github.com/public-clis/bilibili-cli) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [Jina Reader](https://github.com/jina-ai/reader) · [Exa](https://exa.ai) · [mcporter](https://github.com/nicobailon/mcporter) · [feedparser](https://github.com/kurtmckee/feedparser) · [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) · [KittenTTS](https://github.com/KittenML/KittenTTS) · [Free Claude Code](https://github.com/Panniantong/free-claude-code)

## Contacto

- 📧 **Email:** pnt01@foxmail.com
- 🐦 **Twitter/X:** [@Neo_Reidlab](https://x.com/Neo_Reidlab)

Para colaboración o preguntas, agrégame en WeChat — te invitaré al grupo de intercambio:

<p align="center">
  <img src="wechat-group-qr.jpg" width="280" alt="WeChat QR">
</p>

> Para reportar bugs y solicitar funcionalidades, usa [GitHub Issues](https://github.com/Panniantong/Agent-Reach/issues) — es más fácil de rastrear.

## Licencia

[MIT](../LICENSE)

## Enlaces de interés

[Suscripción de modelos Ark Agent Plan](https://dis.chatdesks.cn/chatdesk/hsyqAgent-Reach.html) — Integra los modelos SOTA desarrollados por ByteDance, incluyendo Doubao-Seed, Doubao-Seedance, Doubao-Seedream y más, cubriendo tareas multimodales de texto, código, imágenes y video. Soporta los últimos MiniMax-M3, DeepSeek-V4, GLM-5.2, Doubao-Seed-2.0, Kimi-K2.6 y más, sin restricciones de herramientas. Suscripción única para cambiar entre motores AI según la tarea.

[OpenClaw en Tencent Cloud](https://www.tencentcloud.com/act/pro/intl-openclaw?referral_code=G76Y819A&lang=en&pg=) — Un clic para OpenClaw en Tencent Cloud: conecta Agent Reach por对话 y dale a tu OpenClaw capacidades de internet.

[Mirror AtomGit](https://atomgit.com/qq_51337814/Agent-Reach) — Mirror sincronizado de Agent Reach en AtomGit.

## Historial de Stars

[![Star History Chart](https://api.star-history.com/svg?repos=Panniantong/Agent-Reach&type=Date&v=20260309)](https://star-history.com/#Panniantong/Agent-Reach&Date)
