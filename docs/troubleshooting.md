# Solución de problemas comunes

## Xueqiu / 雪球: API devuelve 400

**Síntoma:** `agent-reach doctor` muestra Xueqiu ⚠️, error `HTTP Error 400`

**Causa:** La API de Xueqiu necesita Cookie de login, no se puede acceder de forma anónima.

**Solución:** Inicia sesión en xueqiu.com en Chrome, luego ejecuta:

```bash
agent-reach configure --from-browser chrome
```

Ejecuta `agent-reach doctor` nuevamente para confirmar que se restauró ✅. Cuando la Cookie expire, solo vuelve a ejecutarlo.

---

## Twitter/X: twitter-cli falla la conexión

**Síntoma:** `twitter search` u otros comandos devuelven error

**Causa:** twitter-cli necesita las variables de entorno AUTH_TOKEN y CT0 para acceder a la API de Twitter. Si tu red necesita proxy para acceder a x.com, necesitas configurarlo.

**Solución:**

### Opción 1: Configurar proxy vía variables de entorno

```bash
export HTTP_PROXY="http://user:pass@host:port"
export HTTPS_PROXY="http://user:pass@host:port"
twitter search "test" -n 1
```

### Opción 2: Usar herramienta de proxy global

Que la herramienta de proxy tome control de todo el tráfico de red, así las peticiones de twitter-cli también pasarán por el proxy:

```bash
# macOS — ClashX / Surge activar "modo mejorado"
# Linux — proxychains o tun2socks
proxychains twitter search "test" -n 1
```

### Opción 3: No usar twitter-cli, usar Exa como alternativa

Si twitter-cli no está disponible, puedes usar directamente Exa para buscar contenido de Twitter:

```bash
mcporter call 'exa.web_search_exa(query: "site:x.com término de búsqueda", numResults: 5)'
```

### Opción 4: Verificar autenticación

```bash
twitter check
```

> Si devuelve "Missing credentials", necesitas configurar las variables de entorno AUTH_TOKEN y CT0.
>
> **Respaldo:** Si ya tienes instalado bird CLI (`npm install -g @steipete/bird`), también funciona correctamente. Agent Reach detecta automáticamente las herramientas instaladas.

---

## Reddit: No se puede acceder

**Síntoma:** Comandos de Reddit fallan o agent-reach doctor muestra ❌

**Causa:** Los endpoints anónimos de Reddit están bloqueados. La API oficial requiere aprobación manual. Solo se puede acceder con sesión de login.

**Solución:**

### Opción 1: OpenCLI (recomendada para escritorio)

OpenCLI reutiliza tu sesión del navegador. Solo necesitas haber iniciado sesión en reddit.com en Chrome:

```bash
agent-reach install --channels opencli
# Luego instalar la extensión de Chrome y ejecutar opencli doctor
```

### Opción 2: rdt-cli con Cookie

```bash
# Instalar rdt-cli
pipx install 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66'

# Login (extrae Cookie del navegador)
rdt login

# Si no tienes navegador (servidor), exporta Cookie con Cookie-Editor y configura:
agent-reach configure reddit-cookie "key1=val1; key2=val2; ..."
```

---

## Xiaohongshu / 小红书: No funciona

**Síntoma:** Búsqueda o lectura de Xiaohongshu falla

**Solución según entorno:**

### Escritorio (OpenCLI)

```bash
agent-reach install --channels opencli
# Instalar extensión de Chrome, ejecutar opencli doctor
```

### Servidor (xiaohongshu-mcp)

```bash
# 1. Descargar binary desde https://github.com/xpzouying/xiaohongshu-mcp/releases
# 2. Iniciar servicio (primera vez descarga ~150MB de navegador headless)
# 3. Escanear QR de login
# 4. Conectar:
mcporter config add xiaohongshu http://localhost:18060/mcp
```

### xhs-cli (legacy)

```bash
# Si ya lo tienes instalado, funciona como respaldo
xhs login

# Si falla, exporta Cookie con Cookie-Editor:
agent-reach configure xhs-cookies "key1=val1; key2=val2; ..."
```

---

## Xiaoyuzhou Podcast: Transcripción falla

**Síntoma:** `transcribe.sh` no funciona o devuelve error

**Causa:** Falta API Key de Groq o no está configurada.

**Solución:**

```bash
# Obtener Key gratis en https://console.groq.com
# (Login con Google/GitHub → API Keys → Create API Key)

# Configurar:
agent-reach configure groq-key gsk_xxxxx
```

**Límites de la cuota gratuita:**
- ~2 horas de audio por hora (7200 segundos)
- Se recupera automáticamente después de 15 minutos
- Para podcasts largos (+2 horas), procesa por partes

---

## LinkedIn: Login falla

**Síntoma:** `linkedin-scraper-mcp --login` no puede abrir el navegador

**Causa:** Necesita interfaz gráfica de navegador.

**Solución:**

### PC de escritorio
```bash
linkedin-scraper-mcp --login --no-headless
# Se abre el navegador, inicia sesión manualmente
```

### Servidor (vía VNC)
```bash
# Instalar VNC
apt install -y tigervnc-standalone-server
vncserver :1 -geometry 1280x720

# Conectar con cliente VNC a IP:5901
# En la terminal del escritorio VNC:
export DISPLAY=:1
linkedin-scraper-mcp --login --no-headless
```

### Iniciar servicio MCP después del login
```bash
linkedin-scraper-mcp --transport streamable-http --port 8001
mcporter config add linkedin http://localhost:8001/mcp
```

---

## Bilibili: yt-dlp bloqueado

**Síntoma:** yt-dlp no funciona para Bilibili (error 412)

**Causa:** Bilibili bloqueó yt-dlp en junio 2026.

**Solución:** Usa bili-cli (ya incluido en Agent Reach):

```bash
bili search "término de búsqueda" --type video
```

Los subtítulos se obtienen vía OpenCLI:

```bash
opencli bilibili subtitle BVxxx
```
