# Agent Reach — Guía de actualización

## Para humanos

Copia esto para tu AI Agent:

```
Actualiza Agent Reach: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

---

## Para AI Agents

### ⚠️ Reglas del directorio de trabajo

**Nunca crees archivos, clones repos o ejecutes comandos en el directorio de trabajo del agent.** Usa `/tmp/` para trabajo temporal y `~/.agent-reach/` para datos persistentes.

### Objetivo

Actualizar Agent Reach a la última versión, refrescar herramientas upstream, migrar de backends retirados y verificar que todo funcione. El usuario no debería necesitar hacer nada manualmente (excepto cosas que solo un humano puede hacer, como hacer clic en un botón de instalación de extensión del navegador).

### Paso 1: Verificar versión actual

```bash
agent-reach check-update
```

Si dice "ya estás en la última versión", salta al Paso 4 (verificación). Si no, continúa.

### Paso 2: Actualizar el paquete Agent Reach

```bash
pip install --upgrade https://github.com/Panniantong/agent-reach/archive/main.zip
```

> Si pip muestra error de `externally-managed-environment` (PEP 668), el usuario
> instaló originalmente con pipx o un venv — usa el comando correspondiente:
> `pipx install --force https://github.com/Panniantong/agent-reach/archive/main.zip`
> o activa `~/.agent-reach-venv` primero.

### Paso 3: Refrescar herramientas upstream

Ejecuta estos comandos para mantener las herramientas instaladas actualizadas. **Solo actualiza lo que ya esté instalado — no instales herramientas nuevas que el usuario nunca pidió** (la única excepción: OpenCLI en escritorio, ver más abajo).

```bash
# CLIs basados en Python que el usuario ya tiene (actualizar mantiene las firmas frescas)
which twitter >/dev/null 2>&1 && { pipx upgrade twitter-cli 2>/dev/null || uv tool upgrade twitter-cli 2>/dev/null; }
which bili    >/dev/null 2>&1 && { pipx upgrade bilibili-cli 2>/dev/null || uv tool upgrade bilibili-cli 2>/dev/null; }
which xhs     >/dev/null 2>&1 && { pipx upgrade xiaohongshu-cli 2>/dev/null || uv tool upgrade xiaohongshu-cli 2>/dev/null; }
which yt-dlp  >/dev/null 2>&1 && { pipx upgrade yt-dlp 2>/dev/null || uv tool upgrade yt-dlp 2>/dev/null || pip install -U yt-dlp 2>/dev/null; }

# rdt-cli está fijado a una fuente git (PyPI va más lento) — misma fijación que _RDT_GIT_SOURCE del código
which rdt >/dev/null 2>&1 && pipx install --force 'git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66' 2>/dev/null

# Basados en npm
which mcporter >/dev/null 2>&1 && npm update -g mcporter 2>/dev/null
which opencli  >/dev/null 2>&1 && npm update -g @jackwener/opencli 2>/dev/null
```

**Usuarios de escritorio sin OpenCLI**: desde la v1.5.0, OpenCLI es el backend preferido para Xiaohongshu/Reddit (y añade subtítulos de Bilibili) aprovechando la sesión del navegador. Ofrécelo una vez:

> "Esta actualización introduce el backend OpenCLI (reutiliza tu login del navegador, Xiaohongshu/Reddit cero configuración). ¿Quieres instalarlo? Solo necesitas hacer clic una vez en 'Añadir extensión' en la Chrome Web Store."

Si sí: `agent-reach install --channels opencli` y guíalo para el clic de la extensión. Si no, todo sigue funcionando con los backends existentes.

### Paso 4: Coexistencia (NO desinstales herramientas viejas)

**Nunca desinstales herramientas que el usuario ya tenga.** Los backends retirados (ej. yt-dlp ya no sirve para Bilibili; xhs-cli ya no se instala por defecto) siguen funcionando como respaldos donde aún funcionan. Agent Reach los evita automáticamente — la eliminación es decisión del usuario, no tuya.

### Paso 5: Verificar

```bash
agent-reach version
agent-reach doctor
```

Ejecutar `agent-reach doctor` (modo texto) también asegura que exista un skill de Agent Reach en los directorios de skills del agent detectados. Si el usuario ya tiene un skill ahí, doctor lo preserva en lugar de sobrescribir personalizaciones locales. Usa `agent-reach skill --install` cuando quieras explícitamente refrescar los archivos skill incluidos.

Revisa la salida de doctor:

- Cada canal muestra ✅ / [!] con un mensaje claro, y los canales con múltiples backends (Xiaohongshu/Reddit/Bilibili/Twitter) reportan `backend actual: …`
- Si un canal que antes funcionaba ahora muestra [X]/error, el mensaje contiene la solución exacta (ej. receta de reinstalar venv) — ejecútala y vuelve a verificar
- `--json` da los mismos datos en formato máquina (`active_backend` por canal)

### Paso 6: Reportar al usuario

Dile al usuario:

1. En qué versión está ahora (`agent-reach version`)
2. Cuántos canales están disponibles y qué backend está usando cada plataforma con múltiples backends (de doctor)
3. Algo que necesite su acción (ej. clic en extensión de Chrome, `xhs login`, escanear QR para xiaoyuzhou-mcp en servidores)
4. Qué cambió en esta actualización (notas de release que muestra `check-update`)

Listo.
