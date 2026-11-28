# VentaReparacionPC (web del taller)

Sitio estático generado con Python, publicado con GitHub Pages desde `docs/`.

## Estructura

```
docs/        Lo que se publica (HTML generado, assets/, robots.txt, sitemap.xml, favicon…). No se edita a mano.
  assets/    css/ (solo .min.css), js/, img/ (webp + logo.svg), icons/
src/         Fuentes del sitio
  css/       style.css, home.css  (build.py los minifica a docs/assets/css/)
  templates/ home_sections.html
tools/       Scripts: build.py (genera docs/), legal.py (textos legales), make_icons.py, optimizar_imagenes.py
data/        pcs.json (fichas de los PC gaming)
local/       Solo en el PC de trabajo, ignorado por Git (fuentes antiguas, copias, prototipos, notas)
.claude/     Configuración local de Claude Code (ignorada por Git)
```

## Flujo de trabajo

1. Editar `src/`, `data/` o los textos de `tools/build.py` / `tools/legal.py`.
2. `python tools/build.py` regenera `docs/`.
3. Vista previa: `python -m http.server 8791 --directory docs` y abrir http://127.0.0.1:8791/.

## Notas

- Los HTML sueltos de `docs/` con nombres antiguos (p. ej. `actualizacion-bios.html`, `ryzen-…r.l..html`) son **redirecciones** hacia las URLs nuevas; `build.py` las genera a partir de `REDIRECTS` y de las fichas de `data/pcs.json`. Deben quedarse en la raíz de `docs/` para que las URLs de la web antigua sigan funcionando.
- Web en modo `noindex` hasta el lanzamiento (`INDEXAR` en `tools/build.py`).
- Secretos en `.env` (ignorado); plantilla en `.env.example`.
