#!/usr/bin/env python3
"""Genera el sitio estático (HTML) de VRPC en la raíz del repo.
Uso:  python tools/build.py
Lee las fichas de PC desde varios/sitio (solo local) la primera vez y deja
los datos en data/pcs.json; después ya no hace falta 'varios/'."""
import html, json, re, shutil, struct, sys
from pathlib import Path
from urllib.parse import urljoin
sys.path.insert(0, str(Path(__file__).resolve().parent))
import legal   # textos legales (tools/legal.py)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "varios" / "sitio"
IMG = ROOT / "assets" / "img"
TEL = "622 22 97 95"
TEL_LINK = "tel:+34622229795"
WA = "https://wa.me/34622229795"
MAIL = "info@ventareparacionpc.es"
DIR = "Carrer de les Aigües del Llobregat, 115, interior<br>08906 L'Hospitalet de Llobregat, Barcelona"
MAPS = "https://www.google.com/maps/search/?api=1&query=Carrer+de+les+Aig%C3%BCes+del+Llobregat+115+L%27Hospitalet+de+Llobregat"
E = html.escape

# ---------------------------------------------------------------- SEO
SITE = "https://ventareparacionpc.es"   # dominio definitivo: canonical, sitemap y datos estructurados
INDEXAR = False                         # poner True SOLO el día del lanzamiento (quita el noindex de todas las páginas)
NEGOCIO = "VentaReparacionPC"
CALLE, CP, CIUDAD, PROVINCIA = "Carrer de les Aigües del Llobregat, 115, interior", "08906", "L'Hospitalet de Llobregat", "Barcelona"
# Horario publicado en la web antigua. COMPROBAR que coincide con la ficha de Google Maps antes de lanzar.
HORARIO = (["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "10:00", "21:00")
OG_IMG = "assets/img/CAJA-ARGB-7-VENT.---11.webp"
OG_ALT = "PC gaming con caja de cristal y ventiladores ARGB"
# URLs de la web antigua (sitemap de ventareparacionpc.es) -> página nueva. Se generan páginas de redirección.
REDIRECTS = {
    "servicio-tecnico.html": "servicios.html",
    "mantenimiento-pc.html": "servicio/mantenimiento-pc-gaming.html",
    "servicio-de-montaje.html": "servicio/servicio-de-montaje.html",
    "asistencia-remota.html": "servicio/asistencia-remota.html",
    "asesoramiento-compra.html": "servicio/asesoramiento-compra.html",
    "convertir-documentos.html": "servicio/convertir-documentos.html",
    "actualizacion-bios.html": "servicio/actualizacion-bios.html",
    "pc-gaming-amd.html": "pc-gaming.html#amd",
    "pc-gaming-intel.html": "pc-gaming.html#intel",
}
SITEMAP = []   # páginas reales escritas (no redirecciones)

def ld(obj):
    """Bloque JSON-LD (datos estructurados para Google)."""
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"

def negocio_ld():
    return ld({"@context": "https://schema.org", "@type": "LocalBusiness", "@id": SITE + "/#negocio", "name": NEGOCIO,
               "url": SITE + "/", "image": f"{SITE}/{OG_IMG}", "logo": f"{SITE}/assets/logo.svg",
               "telephone": "+34" + TEL.replace(" ", ""), "email": MAIL,
               "address": {"@type": "PostalAddress", "streetAddress": CALLE, "postalCode": CP, "addressLocality": CIUDAD,
                           "addressRegion": PROVINCIA, "addressCountry": "ES"},
               "hasMap": MAPS, "areaServed": [CIUDAD, PROVINCIA],
               "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": HORARIO[0], "opens": HORARIO[1], "closes": HORARIO[2]}]})

# ---------------------------------------------------------------- datos de PCs
def load_pcs():
    data = ROOT / "data" / "pcs.json"
    if SRC.exists():
        pcs = []
        for f in sorted(SRC.glob("*r.l*.html")):
            s = f.read_text(encoding="utf-8", errors="ignore")
            body = re.sub(r"<script.*?</script>|<style.*?</style>", "", s[s.find("<body"):], flags=re.S)
            tx = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
            desc = re.findall(r'name="description" content="(.*?)"', s)[0]
            desc = desc.replace("Core Ultra 7 225F", "Core Ultra 5 225F")   # error heredado de la web antigua: el 225F es un Core Ultra 5
            price = re.findall(r"Precio sin descuento\s*([\d\.]+) €", tx)[0]
            name = f.stem.rstrip(".")
            # nombre legible a partir del nombre del archivo
            n = name.replace("-", " ").replace("  ", " ")
            n = re.sub(r"\bintel ultra (\d+) (\d+\w*)", r"Intel Ultra \1 \2", n)
            title = re.sub(r"\s+r l\s*$", " R.L.", n.strip(), flags=re.I)
            title = title.replace("ryzen", "Ryzen").replace("rtx", "RTX").replace("rx ", "RX ").replace("intel i5", "Intel i5")
            title = re.sub(r"\b(\d+) (tb|gb)\b", lambda m: f"{m.group(1)} {m.group(2).upper()}", title)
            title = re.sub(r"(\d)(tb|gb)\b", lambda m: f"{m.group(1)} {m.group(2).upper()}", title)
            title = re.sub(r"\b(\d{4}) (ti)\b", r"\1 Ti", title).replace("5060ti", "5060 Ti").replace("5070 ti", "5070 Ti")
            title = title.replace("x3d", "X3D").replace("7600x", "7600X").replace("7700x", "7700X").replace("7800X3D", "7800X3D")
            title = title.replace("7500f g", "7500F G").replace("9700x", "9700X").replace("7900x", "7900X").replace("9950X3D", "9950X3D")
            title = re.sub(r"(?<=\d)(f|kf|k)\b", lambda m: m.group(1).upper(), title)
            title = title.replace("video", "Video").replace(" a RTX", " A RTX").replace("Ti ", "Ti ").strip()
            title = title.replace("R.L.", "R.L.").replace("R.L", "R.L.").replace("R.L..", "R.L.")
            case = [i for i in re.findall(r"images/([^\"']+)", body)
                    if i.split("---")[0].lower().startswith(("antec", "abysm", "nzxt", "caja", "phanteks", "gigabyte-c500", "msi-mag-pano", "msi-mag-forge", "msi-mpg-velox", "600", "danube"))][0]
            if case.upper().startswith('ANTEC-C8---'): case = 'Antec-C8-Full---1--1-.webp'
            title = re.sub(r"\s+r\.?l\.?$", " R.L.", title, flags=re.I)
            title = re.sub(r"RTX(\d)", r"RTX \1", title)
            title = re.sub(r"\bti\b", "Ti", title).replace(" xt", " XT")
            title = re.sub(r"\s+", " ", title)
            pcs.append(dict(slug=re.sub(r"[^a-z0-9]+", "-", f.stem.lower()).strip("-"), old=f.name, title=title,
                            brand="Intel" if "intel" in f.stem.lower() else "AMD",
                            price=price, desc=desc, img=case))
        data.parent.mkdir(exist_ok=True)
        data.write_text(json.dumps(pcs, ensure_ascii=False, indent=1), encoding="utf-8")
    return json.loads(data.read_text(encoding="utf-8"))

# ------------------------------------------------------------------ contenido
SERVICES = [
    dict(slug="mantenimiento-pc-gaming", t="Mantenimiento PC Gaming", d="Limpieza interna, pasta térmica y revisión de la refrigeración.", img="Mantenimiento-PC-Gaming---6.webp", main=True, icon="fan",
         alt="Técnico aplicando pasta térmica al procesador durante el mantenimiento de un PC Gaming",
         p=["Con el tiempo el polvo se acumula en filtros, ventiladores y disipadores, y el equipo sube de temperatura y hace más ruido. Hacemos una limpieza interna cuidadosa y revisamos la refrigeración.",
            "Cambiamos la pasta térmica cuando hace falta, revisamos ventiladores y flujo de aire y comprobamos temperaturas antes y después."],
         steps=["Limpieza interna de polvo (filtros, ventiladores, disipador)", "Revisión de la refrigeración y del flujo de aire", "Pasta térmica si procede", "Comprobación de temperaturas"],
         extra="Mantenimiento desde 70 €. Te damos el presupuesto antes de empezar."),
    dict(slug="actualizacion-pc-gaming", t="Actualización de PC Gaming", d="Amplía la RAM, instala un SSD o cambia la gráfica.", img="TECNICO-INFORMATICO---10--1-.webp", main=True, icon="chart",
         alt="Técnico informático revisando componentes y cableado dentro de un PC Gaming en el taller",
         p=["Si tu PC ya no rinde como antes, a veces basta con cambiar una pieza. Te ayudamos a elegir qué actualizar primero según lo que usas y tu presupuesto.",
            "Comprobamos la compatibilidad con tu placa, fuente y caja antes de comprar nada."],
         steps=["Revisión del equipo y de lo que necesitas", "Propuesta de componentes compatibles", "Instalación y pruebas", "Comprobación final de rendimiento"],
         extra="Cuéntanos modelo y uso y te orientamos."),
    dict(slug="actualizacion-bios", t="Actualización de BIOS", d="Comprobación del firmware y de la compatibilidad de tu placa base.", img="Actulizacion-BIOS---2_800x800.webp", icon="wrench",
         alt="Portátil mostrando una barra de progreso al 75 % de actualización del sistema, con herramientas de taller alrededor",
         p=["Una BIOS actualizada puede ser necesaria para admitir un procesador nuevo o corregir fallos. Es una operación delicada: la hacemos comprobando antes la versión y la compatibilidad de tu placa."], steps=["Identificación de placa y versión", "Comprobación de compatibilidad", "Actualización controlada", "Verificación de arranque"], extra=""),
    dict(slug="asistencia-remota", t="Asistencia remota", d="Ayuda a distancia para incidencias de software.", img="Asistencia-Remota---3_800x800.webp", icon="wrench",
         m="Asistencia remota para incidencias de software, sistema, programas y configuración: acordamos cita y nos conectamos con tu permiso sin traer el equipo.",
         alt="Monitor con icono de engranaje y herramientas que representa la asistencia remota",
         p=["Para problemas de software (sistema, programas, configuración) podemos ayudarte a distancia sin que tengas que traer el equipo."], steps=["Nos cuentas el problema", "Acordamos cita", "Conexión remota con tu permiso", "Resolución y comprobación"], extra=""),
    dict(slug="asesoramiento-compra", t="Asesoramiento de compra", d="Elige componentes compatibles con tu presupuesto.", img="ASESORAMIENTO-COMPRA-PC---8.webp", icon="wrench",
         m="Te ayudamos a elegir componentes compatibles con tu presupuesto, juegos y programas en L'Hospitalet, con comprobación y opción de montaje.",
         alt="Componentes de PC Gaming (placa base, tarjeta gráfica, refrigeración líquida y caja) en banco de taller",
         p=["Antes de comprar piezas o un equipo, te ayudamos a elegir componentes compatibles entre sí y ajustados a tu presupuesto y a tus juegos o programas."], steps=["Presupuesto y uso", "Selección de componentes", "Comprobación de compatibilidad", "Opción de montaje en el taller"], extra=""),
    dict(slug="servicio-de-montaje", t="Servicio de montaje", d="Montaje y pruebas de los componentes de tu PC.", img="Montaje-PC-Gaming---9.webp", icon="wrench",
         m="Montaje de PC en L'Hospitalet con los componentes que tienes o elijas: cableado, instalación y pruebas antes de la entrega con cita previa.",
         alt="Técnico montando un procesador en la placa base junto a tarjetas gráficas en el taller",
         p=["Montamos tu PC con los componentes que ya tienes o con los que elijas, gestionamos los cables y probamos el equipo antes de entregarlo."], steps=["Recepción de componentes", "Montaje y cableado", "Instalación y pruebas", "Entrega con cita previa"], extra=""),
    dict(slug="convertir-documentos", t="Conversión de documentos", d="Ayuda con archivos que necesitas abrir o cambiar de formato.", img="CONVERTIR-DOCUMENTOS---1.webp", icon="wrench",
         alt="Gráfico de conversión de documentos (DOC, PDF, XLS, PPT) y fotos (JPG, PNG, GIF, RAW)",
         p=["Te ayudamos a abrir o convertir documentos y fotos entre formatos habituales (DOC, PDF, XLS, PPT, JPG, PNG…)."], steps=["Nos traes o envías el archivo", "Conversión al formato que necesitas", "Comprobación del resultado"], extra=""),
]
BLOG = [
    dict(slug="cuando-necesita-mantenimiento-tu-pc-gaming", cat="Mantenimiento", t="¿Cuándo necesita mantenimiento tu PC Gaming?", d="Tres señales que puedes observar mientras juegas y qué información llevar al taller.", img="Mantenimiento-PC-Gaming---6.webp",
         alt="Técnico aplicando pasta térmica al procesador durante el mantenimiento de un PC Gaming",
         sections=[("Fíjate en los cambios", "El polvo visible en los filtros, los ventiladores que hacen más ruido de lo habitual y un equipo que se calienta más con el mismo juego son buenas razones para revisar la refrigeración."),
                   ("Compara en condiciones parecidas", "Anota qué juegos usabas, cuándo empezó el cambio y si pasa siempre o solo después de un rato. Si tienes mediciones de temperatura anteriores, compáralas con el mismo juego y ajustes similares. La temperatura ambiente también influye."),
                   ("¿Limpieza o diagnóstico?", "Una limpieza preventiva puede tener sentido si encuentras polvo acumulado y el equipo funciona bien. Si hay apagados, bloqueos o el ventilador deja de girar, describe el síntoma al pedir cita para que se pueda valorar la causa.")]),
    dict(slug="que-actualizar-primero-en-tu-pc-gaming", cat="Actualizaciones", t="¿Qué actualizar primero en tu PC Gaming?", d="Cómo decidir entre ampliar la RAM, instalar un SSD o cambiar la tarjeta gráfica.", img="Montaje-PC-Gaming---9.webp",
         alt="Técnico instalando componentes en una placa base junto a tarjetas gráficas para actualizar un PC Gaming",
         sections=[("Empieza por el cuello de botella", "Observa qué falla: si tarda en cargar, un SSD puede ayudar; si va justo de memoria al abrir varias cosas, la RAM; si los fotogramas por segundo caen en juegos exigentes, suele ser la gráfica."),
                   ("Comprueba la compatibilidad", "Antes de comprar, revisa tu placa base, la fuente de alimentación y el espacio de la caja. Una pieza potente no sirve si no es compatible con el resto."),
                   ("Pide asesoramiento", "Si dudas, cuéntanos tu equipo y tu presupuesto y te orientamos sobre qué mejora compensa más.")]),
    dict(slug="que-significan-los-led-de-la-placa-base", cat="Diagnóstico", t="¿Qué significan los LED de la placa base?", d="Qué comprobar si una luz de diagnóstico se queda encendida al arrancar.", img="MSI-MAG-B860-TOMAHAWK-WIFI---2_800x800.webp",
         alt="Placa base MSI MAG B860 Tomahawk WiFi con sus ranuras de memoria, socket y conectores",
         sections=[("Busca CPU, DRAM, VGA y BOOT", "Muchas placas tienen cuatro LED de diagnóstico que indican en qué fase se detiene el arranque: procesador, memoria, gráfica o dispositivo de arranque."),
                   ("Qué comprobar primero", "Reasienta la memoria y la gráfica, revisa los cables de alimentación y desconecta lo que no sea imprescindible. Consulta el manual de tu placa para el significado exacto."),
                   ("Cuándo traerlo al taller", "Si el LED sigue encendido tras las comprobaciones básicas, descríbenos qué luz es y qué pasa al arrancar para valorar la causa.")]),
]
NAV = [("index.html", "Inicio"), ("servicios.html", "Servicios"), ("trabajos-realizados.html", "Trabajos realizados"), ("opiniones.html", "Opiniones"), ("pc-gaming.html", "PC Gaming"), ("blog.html", "Blog"), ("contacto.html", "Contacto")]
# Submenús desplegables (hover/teclado en escritorio, botón en móvil)
SUB = {
    "servicios.html": [(f"servicio/{s['slug']}.html", s["t"]) for s in SERVICES] + [("servicios.html", "Ver todos los servicios")],
    "pc-gaming.html": [("pc-gaming.html#todos", "Todos los equipos"), ("pc-gaming.html#amd", "AMD Ryzen"), ("pc-gaming.html#intel", "Intel")],
}

def nav_html(p, active):
    out = []
    for h, t in NAV:
        a = f'<a href="{p}{h}"{" class=\"on\" aria-current=\"page\"" if h == active else ""}>{t}</a>'
        if h in SUB:
            items = "".join(f'<a href="{p}{x}">{y}</a>' for x, y in SUB[h])
            a = f'<div class="has-sub">{a}<button class="sub-t" type="button" aria-expanded="false" aria-label="Mostrar submenú de {t}"></button><div class="sub">{items}</div></div>'
        out.append(a)
    return "".join(out)

ICONS = {
    "cal": '<path d="M7 3v3M17 3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A15 15 0 0 1 4 5a1 1 0 0 1 1-1z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "doc": '<path d="M7 3h8l4 4v14H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "fan": '<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 1-6 3-6s2 3-1 5M14 12c4 0 6 1 6 3s-3 2-5-1M12 14c0 4-1 6-3 6s-2-3 1-5M10 12c-4 0-6-1-6-3s3-2 5 1"/>',
    "chart": '<path d="M4 20h16M7 16v-5M12 16V8M17 16v-8"/>',
    "wrench": '<path d="M14 6a4 4 0 0 0 5 5l-9 9a2 2 0 0 1-3-3l9-9a4 4 0 0 0-2-2z"/>',
    "pc": '<rect x="6" y="3" width="12" height="18" rx="1"/><circle cx="12" cy="9" r="2"/><path d="M9 16h6"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
    "pin": '<path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "alert": '<circle cx="12" cy="12" r="8"/><path d="M12 8v5M12 16v.5"/>',
    "check": '<circle cx="12" cy="12" r="8"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/>',
    "zoom": '<circle cx="10" cy="10" r="5"/><path d="M14 14l5 5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "wa": '<path d="M4 20l1.3-4.2A8 8 0 1 1 8.4 19z"/>',
}
def ic(n, cls=""):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[n]}</svg>'

def asset_img(name):
    src = SRC / "images" / name
    dst = IMG / name
    if src.exists() and not dst.exists():
        shutil.copy(src, dst)
    return f"assets/img/{name}"

_IMG_SIZE = {}
def img_size(name):
    if name not in _IMG_SIZE:
        asset_img(name)
        data = (IMG / name).read_bytes()
        w = h = None
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            chunk = data[12:16]
            if chunk == b"VP8X":
                w = 1 + int.from_bytes(data[24:27], "little")
                h = 1 + int.from_bytes(data[27:30], "little")
            elif chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
                w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
                h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
            elif chunk == b"VP8L" and data[20] == 0x2F:
                bits = struct.unpack("<I", data[21:25])[0]
                w = (bits & 0x3FFF) + 1
                h = ((bits >> 14) & 0x3FFF) + 1
        elif data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data):
                if data[i] != 0xFF:
                    break
                while i < len(data) and data[i] == 0xFF:
                    i += 1
                if i >= len(data):
                    break
                marker = data[i]
                i += 1
                if marker in (0xD8, 0xD9, 0x01) or (0xD0 <= marker <= 0xD7):
                    continue
                length = struct.unpack(">H", data[i:i + 2])[0]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 3:i + 7])
                    break
                i += length
        elif data[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", data[16:24])
        _IMG_SIZE[name] = (w, h) if (w and h) else None
    return _IMG_SIZE[name]

def img_dims(name):
    sz = img_size(name)
    return f' width="{sz[0]}" height="{sz[1]}"' if sz else ""

def trim_meta(text, limit=155, min_len=110):
    s = re.sub(r"\s+", " ", text).strip()
    if len(s) <= limit:
        return s
    for m in reversed(list(re.finditer(r"\.\s+", s))):
        end = m.start() + 1
        if min_len <= end <= limit:
            cand = s[:end].rstrip()
            if not re.search(r"(?:^|\s)(?:[A-Za-z]\.|[A-Za-z]\.[A-Za-z]\.)$", cand):
                return cand
    cut = s[:limit + 1]
    sp = cut.rfind(" ")
    cand = (cut[:sp] if sp > 0 else s[:limit]).rstrip(" ,;:+/-")
    while re.search(r"(?:^|\s)(?:[A-Za-z]\.?|de|y|con|en|a|el|la|los|las|para|por|R\.L\.)$", cand, flags=re.I) and " " in cand:
        cand = cand.rsplit(" ", 1)[0].rstrip(" ,;:+/-")
    return cand

# ------------------------------------------------------------------ plantilla
# Carga anticipada (Speculation Rules): prefetch moderado de enlaces internos al pasar el ratón; no es JS.
SPEC_RULES = ('<script type="speculationrules">{"prefetch":[{"where":{"and":[{"href_matches":"/*"},'
              '{"not":{"selector_matches":"[rel~=nofollow]"}}]},"eagerness":"moderate"}]}</script>')

# Reseñas de Google. Datos a confirmar con Jose antes del lanzamiento (nota/total son los que él indica; la fecha debe ser la de la consulta).
# escribir = enlace de Google para dejar una reseña (https://search.google.com/local/writereview?placeid=...); sin él, el botón no se muestra.
RES = dict(nota="4,9", total="casi 300", fecha=None, escribir=None)
# Reseñas reales copiadas de la ficha de Google, una por elemento: {"texto": "...", "autor": "María G.", "fecha": "octubre 2026", "url": "https://..."}
RESENAS = []

def reviews_block():
    stars = ic("star") * 5
    fecha = f" · a fecha de {E(RES['fecha'])}" if RES["fecha"] else ""
    escribir = f'<a class="btn ghost" href="{E(RES["escribir"])}" rel="noopener">{ic("star")}Dejar una opinión</a>' if RES["escribir"] else ""
    head = (f'<div class="rv-head"><div class="rv-badge"><span class="rv-score">{E(RES["nota"])}</span><div>'
            f'<div class="rv-stars" role="img" aria-label="Valoración de {E(RES["nota"])} sobre 5">{stars}</div>'
            f'<p class="rv-sub">{E(RES["total"])} opiniones en Google{fecha}</p></div></div>'
            f'<div class="btns"><a class="btn" href="{MAPS}" rel="noopener">Ver todas en Google {ic("arrow")}</a>{escribir}</div></div>')
    if RESENAS:
        cards = "".join(
            f'<figure class="card rv-card"><div class="rv-stars" aria-hidden="true">{stars}</div><blockquote><p>{E(r["texto"])}</p></blockquote>'
            f'<figcaption>{E(r["autor"])} · {E(r["fecha"])}'
            + (f' · <a href="{E(r["url"])}" rel="noopener">Ver en Google</a>' if r.get("url") else "") + '</figcaption></figure>'
            for r in RESENAS)
    else:
        ph = '<figure class="card rv-card ph"><div class="rv-stars" aria-hidden="true">' + stars + '</div><blockquote><p><mark class="pend">[PENDIENTE: texto de una reseña real de Google]</mark></p></blockquote><figcaption><mark class="pend">[Nombre · mes y año]</mark></figcaption></figure>'
        cards = ph * 3
    return head + f'<div class="rv-grid">{cards}</div>'

# Barra flotante inferior (solo móvil, ≤960px; mismo patrón que la landing de verstats): flecha ↑ al inicio, Llamar y Pedir cita. Lógica en assets/js/main.js.
MOBILE_BAR = (
    '<aside class="m-bar" id="m-bar" aria-label="Contacto rápido"><div class="m-info"><b>VRPC</b><span>Servicio técnico de PC</span></div>'
    '<div class="m-act"><button type="button" class="m-up" id="m-up" aria-label="Volver arriba"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="18 15 12 9 6 15"/></svg></button>'
    f'<a class="m-btn call" href="{TEL_LINK}" aria-label="Llamar al taller">{ic("phone")}<span>Llamar</span></a>'
    f'<a class="m-btn wa" href="{WA}" rel="noopener" aria-label="Pedir cita por WhatsApp">{ic("wa")}<span>Pedir cita</span></a></div></aside>')

def reviews_home():
    return ('\n<section class="rv" id="opiniones" aria-labelledby="rv-title"><div class="wrap"><p class="kicker">Opiniones</p>'
            f'<h2 id="rv-title">Lo que dicen quienes ya nos han visitado</h2>{reviews_block()}</div></section>\n')

def page(path, title, desc, body, active="", depth=0, extra_head="", hero=False, solo=False, img=None, og_type="website", img_alt=None, is_404=False):
    p = "../" * depth
    robots = "noindex, nofollow" if is_404 else ("index, follow, max-image-preview:large" if INDEXAR else "noindex, nofollow")
    base_head = ('<script>(function(){var b=\'/\';if(location.hostname.endsWith(\'.github.io\')){var m=location.pathname.match(/^\\/([^/]+)/);if(m)b=\'/\'+m[1]+\'/\';}var el=document.createElement(\'base\');el.href=b;document.head.appendChild(el);})();</script>'
                 '<noscript><base href="/"></noscript>') if is_404 else ""
    if is_404:
        seo = '<meta name="theme-color" content="#1d5fd1">'
    else:
        og_rel = img or OG_IMG
        sz = img_size(Path(og_rel).name)
        og_dims = f'<meta property="og:image:width" content="{sz[0]}"><meta property="og:image:height" content="{sz[1]}">' if sz else ""
        # %%URL%% se sustituye en write() por la URL canónica de cada página
        seo = (f'<link rel="canonical" href="%%URL%%"><meta property="og:type" content="{og_type}"><meta property="og:locale" content="es_ES">'
               f'<meta property="og:site_name" content="{NEGOCIO}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">'
               f'<meta property="og:url" content="%%URL%%"><meta property="og:image" content="{SITE}/{og_rel}">{og_dims}'
               f'<meta property="og:image:alt" content="{E(img_alt or OG_ALT)}">'
               f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}">'
               f'<meta name="twitter:description" content="{E(desc)}"><meta name="theme-color" content="#1d5fd1">')
    icons = (f'<link rel="icon" href="{p}favicon.ico" sizes="16x16 32x32 48x48">'
             f'<link rel="icon" href="{p}assets/logo.svg" type="image/svg+xml">'
             f'<link rel="icon" href="{p}assets/icons/icon-192.png" type="image/png" sizes="192x192">'
             f'<link rel="icon" href="{p}assets/icons/icon-512.png" type="image/png" sizes="512x512">'
             f'<link rel="apple-touch-icon" href="{p}apple-touch-icon.png" sizes="180x180">')
    skip = "" if is_404 else '<a class="skip" href="#main">Saltar al contenido</a>'
    nav = nav_html(p, active)
    cta = f"""<section class="cta"><div class="wrap cta-in"><div><h2>¿Tu ordenador necesita revisión?</h2><p>Cuéntanos qué le ocurre y pide cita en L'Hospitalet.</p></div>
<div class="btns"><a class="btn white" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost-w" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div></div></section>"""
    foot = f"""<footer class="foot"><div class="wrap foot-in"><div><strong>VENTAREPARACIONPC</strong><br><span>L'Hospitalet de Llobregat · {TEL}</span></div>
<nav aria-label="Pie"><a href="{p}contacto.html">Contacto</a><a href="{p}ubicacion.html">Ubicación</a><a href="{p}blog.html">Blog</a><a href="{p}aviso-legal.html">Aviso legal</a><a href="{p}politica-de-cookies.html">Política de cookies</a></nav></div></footer>"""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{base_head}
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="robots" content="{robots}">
{seo}
{icons}<link rel="stylesheet" href="{p}assets/css/style.css">{extra_head}{SPEC_RULES}</head>
<body{" class=\"solo\"" if solo else ""}>{skip}
<header class="top"><div class="wrap top-in"><a class="brand" href="{p}index.html" aria-label="VRPC Ventareparacionpc, inicio"><img src="{p}assets/logo.svg" alt="VRPC Ventareparacionpc" width="140" height="42"></a>
<button type="button" class="burger" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
<nav id="nav" class="nav" aria-label="Principal">{nav}<a class="btn small mob-only" href="{WA}">{ic("cal")}Pedir cita</a></nav>
<a class="btn small desk-only" href="{WA}">{ic("cal")}Pedir cita</a><div class="nav-ov" id="nav-ov" aria-hidden="true"></div></div></header>
<div class="draft-tag" role="note">Borrador de diseño</div><main id="main">{body}</main>{"" if solo else cta}{"" if solo else foot}{"" if (solo or is_404) else MOBILE_BAR}<script src="{p}assets/js/main.js" defer></script></body></html>"""

def head_band(crumbs, h1, sub=""):
    c = " <span>›</span> ".join(f'<a href="{h}">{t}</a>' if h else f"<span>{t}</span>" for h, t in crumbs)
    # migas para Google; "REL:" se convierte en URL absoluta en write()
    items = [dict({"@type": "ListItem", "position": i + 1, "name": html.unescape(t)}, **({"item": "REL:" + h} if h else {}))
             for i, (h, t) in enumerate(crumbs)]
    bc = ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    return f'<section class="band"><div class="wrap"><nav class="crumbs" aria-label="Migas">{c}</nav><h1>{h1}</h1>{f"<p>{sub}</p>" if sub else ""}</div>{bc}</section>'

def svc_card(s, p="", h="h3"):
    # h="h2" cuando la tarjeta cuelga directamente del h1 (la clase h3 conserva su tamaño visual)
    tag = f'<h2 class="h3">{s["t"]}</h2>' if h == "h2" else f"<h3>{s['t']}</h3>"
    return f"""<a class="card svc" href="{p}servicio/{s['slug']}.html"><img src="{p}{asset_img(s['img'])}" alt="" loading="lazy"{img_dims(s['img'])}><div class="svc-t">{ic(s['icon'])}{tag}<p>{s['d']}</p><span class="more">Más información {ic("arrow")}</span></div></a>"""

def url_of(path):
    return SITE + "/" if path == "index.html" else f"{SITE}/{path}"

def write(path, content):
    if "%%URL%%" in content:   # página real: URL canónica, migas absolutas y entrada en el sitemap
        base = url_of(path)
        content = content.replace("%%URL%%", base)
        content = re.sub(r'"REL:([^"]*)"', lambda m: json.dumps(url_of(urljoin(f"{SITE}/{path}", m.group(1))[len(SITE) + 1:])), content)
        SITEMAP.append(path)
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

def write_redirect(old, new):
    """Página en la URL antigua que lleva a la nueva (Google trata el refresh inmediato como redirección permanente)."""
    write(old, f'<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><title>Página trasladada | {NEGOCIO}</title><meta name="robots" content="noindex">'
               f'<link rel="canonical" href="{url_of(new.split("#")[0])}"><meta http-equiv="refresh" content="0; url={new}"></head>'
               f'<body><p>Esta página se ha trasladado a <a href="{new}">{url_of(new.split("#")[0])}</a>.</p></body></html>')

def build():
    IMG.mkdir(parents=True, exist_ok=True)
    pcs = load_pcs()
    hero = asset_img("PC-INTEL-A-MEDIDA---8.webp")
    main_s = [s for s in SERVICES if s.get("main")]
    other_s = [s for s in SERVICES if not s.get("main")]

    # ---- Inicio
    steps = [("pc", "Traes tu equipo", "Nos cuentas qué le pasa a tu ordenador."), ("search", "Revisión delante de ti", "Comprobamos el equipo contigo."), ("chat", "Explicación clara", "Te contamos qué vemos y qué opciones tienes."), ("doc", "Presupuesto", "Valoramos el coste antes de empezar el trabajo.")]
    st = "".join(f'<li><span class="n">{i+1}</span>{ic(ic_)}<strong>{a}</strong><small>{b}</small></li>' for i, (ic_, a, b) in enumerate(steps))
    body = f"""<section class="hg" id="hero"><div class="hg-c">
<div class="hg-l">
<div class="hg-top"><p class="hg-kick">Servicio técnico en L'Hospitalet de Llobregat</p>
<h1>Expertos en <em>Reparación y Montaje</em> de Ordenadores</h1>
<p class="hg-sum">En VentaReparacionPC cuidamos de tu equipo como si fuera nuestro.</p></div>
<div class="hg-proc"><p class="hg-eb">Así trabajamos</p><h2>Servicio técnico transparente</h2><p class="hg-ps">Un proceso claro y sencillo para que siempre sepas qué le ocurre a tu equipo y qué soluciones tiene.</p>
<ol class="hg-st"><li><span class="n">1</span><span class="ico">{ic("pc")}</span><b>Traes tu equipo</b><span class="d">Nos cuentas el problema y revisamos tu PC Gaming.</span></li><li class="ar" aria-hidden="true">{ic("arrow")}</li><li><span class="n">2</span><span class="ico">{ic("search")}</span><b>Revisión delante de ti</b><span class="d">Analizamos el hardware delante del cliente.</span></li><li class="ar" aria-hidden="true">{ic("arrow")}</li><li><span class="n">3</span><span class="ico">{ic("chat")}</span><b>Explicación clara</b><span class="d">Te mostramos el origen del problema y las posibles soluciones.</span></li><li class="ar" aria-hidden="true">{ic("arrow")}</li><li><span class="n">4</span><span class="ico">{ic("doc")}</span><b>Presupuesto al momento</b><span class="d">Te damos el precio en el acto, sin compromiso.</span></li></ol></div>
<div class="hg-bot"><p class="hg-small">Nos especializamos en la reparación de ordenadores de sobremesa de todas las marcas, resolviendo problemas de lentitud, fallos de arranque o de placa base. Además, somos apasionados del hardware. Diseñamos tu PC Gaming personalizado pieza a pieza, optimizando cada euro de tu presupuesto para ofrecerte el máximo rendimiento en tus juegos favoritos. Todo ello con componentes de primeras marcas y total garantía.</p>
<div class="hg-cta"><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa {ic("arrow")}</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div></div>
</div>
<figure class="hg-r"><img src="assets/img/CAJA-ARGB-7-VENT.---11.webp" alt="PC gaming con caja de cristal y ventiladores ARGB" fetchpriority="high"{img_dims("CAJA-ARGB-7-VENT.---11.webp")}>

</figure>
</div>
<a class="scroll-cue" href="#pantalla-2" id="scrollCue" aria-label="Bajar a Servicio Técnico">Servicio Técnico<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg></a></section>
""" + (ROOT / "tools" / "home_sections.html").read_text(encoding="utf-8") + reviews_home()
    write("index.html", page("index.html", "VRPC · Reparación y PC Gaming en L'Hospitalet", "Servicio técnico, mantenimiento y PC Gaming a medida en L'Hospitalet de Llobregat. Pide cita previa.", body, "index.html", extra_head=negocio_ld() + '<link rel="stylesheet" href="assets/css/home.css"><script src="assets/js/home.js" defer></script>'))

    # ---- Servicios + fichas
    body = head_band([("index.html", "Inicio"), (None, "Servicio técnico")], "Servicio técnico", "Mantenimiento y mejoras de hardware para PC Gaming en L'Hospitalet de Llobregat.") + \
        f'<section class="wrap sec"><div class="g2 big">{"".join(svc_card(s, h="h2") for s in main_s)}</div><h2 class="sp">Otros servicios</h2><div class="g3">{"".join(svc_card(s) for s in other_s)}</div></section>'
    write("servicios.html", page("servicios.html", "Servicio técnico | VRPC", "Servicios de mantenimiento, actualización, BIOS, asistencia remota y montaje de PC en L'Hospitalet.", body, "servicios.html"))
    for s in SERVICES:
        li = "".join(f"<li>{x}</li>" for x in s["steps"])
        body = head_band([("../index.html", "Inicio"), ("../servicios.html", "Servicios"), (None, s["t"])], s["t"], s["d"]) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover" src="../{asset_img(s['img'])}" alt="{E(s['alt'])}" fetchpriority="high">{"".join(f"<p>{x}</p>" for x in s['p'])}<h2>Qué incluye</h2><ul class="list">{li}</ul>{f'<p><strong>{s["extra"]}</strong></p>' if s['extra'] else ''}</article>
<aside class="card side"><h3>Pide cita</h3><p>Cuéntanos el modelo y lo que necesitas. Atendemos con cita previa en L'Hospitalet.</p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></aside></section>""" + \
            ld({"@context": "https://schema.org", "@type": "Service", "name": s["t"], "serviceType": s["t"], "description": s["d"], "url": "%%URL%%",
                "provider": {"@id": SITE + "/#negocio"}, "areaServed": {"@type": "City", "name": CIUDAD}})
        write(f"servicio/{s['slug']}.html", page("", f"{s['t']} | VRPC", s.get("m", s["d"]), body, "servicios.html", 1, extra_head=negocio_ld(), img=asset_img(s["img"]), img_alt=s["alt"]))

    # ---- Trabajos realizados
    body = head_band([("index.html", "Inicio"), (None, "Trabajos realizados")], "Trabajos realizados") + f"""<section class="wrap sec two"><div><h2>Limpieza interna de un PC Gaming</h2>
<div class="ba-g"><figure class="card"><img src="assets/img/antes.jpg" alt="Interior del PC con polvo acumulado" loading="lazy" data-zoom><figcaption>{ic("alert","r")}Antes del mantenimiento{ic("zoom","z")}</figcaption></figure>
<figure class="card"><img src="assets/img/despues.jpg" alt="Interior del PC limpio" loading="lazy" data-zoom><figcaption>{ic("check","g")}Después del mantenimiento{ic("zoom","z")}</figcaption></figure></div>
<p class="muted">Las fotos muestran el interior del equipo antes y después de retirar el polvo acumulado. Pulsa en cualquiera para ampliarla.</p></div>
<aside><div class="card side"><h3>Pide cita para tu equipo</h3><p>Cuéntanos el modelo y lo que necesitas. Atendemos con cita previa en L'Hospitalet.</p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div>
<div class="card side"><h3>Servicio de este trabajo</h3><a class="more row" href="servicio/mantenimiento-pc-gaming.html">Mantenimiento PC Gaming {ic("arrow")}</a></div></aside></section>"""
    write("trabajos-realizados.html", page("", "Trabajos realizados | VRPC", "Ejemplos de trabajos realizados en el taller: antes y después de una limpieza interna de PC Gaming.", body, "trabajos-realizados.html"))

    # ---- Opiniones
    body = head_band([("index.html", "Inicio"), (None, "Opiniones de clientes")], "Opiniones de clientes", "Lee en Google las experiencias que han compartido quienes han pasado por el taller.") + f"""<section class="wrap sec rv-page">{reviews_block()}</section>
<section class="wrap sec">
<aside class="card side"><h2 class="h3">Conoce el taller</h2><a class="more row" href="trabajos-realizados.html">Trabajos realizados {ic("arrow")}</a><a class="more row" href="ubicacion.html">Ubicación {ic("arrow")}</a><a class="more row" href="contacto.html">Contacto {ic("arrow")}</a></aside></section>"""
    write("opiniones.html", page("", "Opiniones de clientes | VRPC", "Opiniones de clientes de VENTAREPARACIONPC en Google.", body, "opiniones.html"))

    # ---- PC Gaming
    cards = "".join(f"""<a class="card pc" href="pc/{c['slug']}.html" data-brand="{c['brand']}" data-t="{E(c['title'].lower())}"><img src="{asset_img(c['img'])}" alt="" loading="lazy"><div class="pc-b"><span class="brand-tag {c['brand'].lower()}">{c['brand'].upper() if c['brand']=='Intel' else 'AMD'}</span><h2 class="h3">{E(c['title'])}</h2><span class="more">Ver ficha {ic("arrow")}</span></div></a>""" for c in pcs)
    body = head_band([("index.html", "Inicio"), (None, "PC Gaming a medida")], "PC Gaming a medida", "Explora las configuraciones AMD e Intel de VRPC. Montamos los equipos bajo pedido.") + f"""<section class="wrap sec"><div class="filters" id="filters"><button type="button" class="chip on" data-f="all">Todos</button><button type="button" class="chip" data-f="AMD">AMD Ryzen</button><button type="button" class="chip" data-f="Intel">Intel</button></div>
<div class="searchrow"><label for="q">Buscar</label><div><input id="q" type="search" placeholder="Por ejemplo, Ryzen 7 o RTX 5070"><span id="count" aria-live="polite">{len(pcs)} resultados</span></div></div>
<div class="g4" id="grid">{cards}</div></section>"""
    write("pc-gaming.html", page("", "PC Gaming a medida | VRPC", "Configuraciones de PC Gaming AMD Ryzen e Intel montadas bajo pedido en L'Hospitalet.", body, "pc-gaming.html"))
    for c in pcs:
        specs = [x.strip() for x in re.split(r"\.\s+", c["desc"]) if x.strip()]
        body = head_band([("../index.html", "Inicio"), ("../pc-gaming.html", "PC Gaming"), (None, E(c["title"]))], E(c["title"])) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover contain" src="../{asset_img(c['img'])}" alt="Caja del equipo {E(c['title'])}" fetchpriority="high"{img_dims(c['img'])}>
<p class="price">{c['price']} € <small>precio sin descuento</small></p><ul class="list">{"".join(f"<li>{E(x.rstrip('.'))}</li>" for x in specs)}</ul>
<ul class="list"><li>Montaje bajo pedido</li><li>Windows 11 Pro licencia oficial (según configuración)</li></ul><p class="muted">Precios de referencia (última actualización conocida: 31-07-26). Confirma disponibilidad y plazo de entrega al pedir cita.</p></article>
<aside class="card side"><h2 class="h3">Pide cita para este equipo</h2><p>Te confirmamos precio, plazo de entrega y posibles cambios de componentes.</p><a class="btn" href="{WA}?text={E(c['title'].replace(' ','%20'))}">{ic("wa")}Consultar por WhatsApp</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></aside></section>"""
        pc_title = f"{c['title']} | PC Gaming VRPC"
        if len(pc_title) > 60:
            pc_title = f"{c['title']} | VRPC"
        write(f"pc/{c['slug']}.html", page("", pc_title, trim_meta(c["desc"]), body, "pc-gaming.html", 1, img=asset_img(c["img"]), img_alt=f"Caja del equipo {c['title']}"))

    # ---- Blog
    bc = "".join(f"""<a class="card post" href="blog/{b['slug']}.html"><img src="{asset_img(b['img'])}" alt="" loading="lazy"><div class="pc-b"><span class="cat">{b['cat']}</span><h2 class="h3">{b['t']}</h2><p>{b['d']}</p></div></a>""" for b in BLOG)
    body = head_band([("index.html", "Inicio"), (None, "Blog")], "Blog", "Guías de VRPC para cuidar, mejorar y entender tu PC Gaming.") + f'<section class="wrap sec"><div class="g3">{bc}</div></section>'
    write("blog.html", page("", "Blog | VRPC", "Guías para cuidar, mejorar y entender tu PC Gaming.", body, "blog.html"))
    for b in BLOG:
        more = "".join(f'<a class="more row" href="{o["slug"]}.html">{o["t"]} {ic("arrow")}</a>' for o in BLOG if o is not b)
        secs = "".join(f"<h2>{h}</h2><p>{t}</p>" for h, t in b["sections"])
        body = head_band([("../index.html", "Inicio"), ("../blog.html", "Blog"), (None, b["cat"])], b["t"], b["d"]) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover" src="../{asset_img(b['img'])}" alt="{E(b['alt'])}" fetchpriority="high">{secs}<p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a></p></article><aside class="card side"><h3>Más guías</h3>{more}</aside></section>""" + \
            ld({"@context": "https://schema.org", "@type": "BlogPosting", "headline": b["t"], "description": b["d"],
                "image": f"{SITE}/{asset_img(b['img'])}", "url": "%%URL%%",
                "mainEntityOfPage": {"@type": "WebPage", "@id": "%%URL%%"}, "inLanguage": "es",
                "author": {"@id": SITE + "/#negocio"}, "publisher": {"@id": SITE + "/#negocio"}})
        write(f"blog/{b['slug']}.html", page("", f"{b['t']} | Blog VRPC", b["d"], body, "blog.html", 1, extra_head=negocio_ld(), img=asset_img(b["img"]), og_type="article", img_alt=b["alt"]))

    # ---- Contacto / ubicación / legales
    body = head_band([("index.html", "Inicio"), (None, "Contacto")], "Contacto", "Contacta con VRPC para concertar una cita antes de traer tu ordenador.") + f"""<section class="wrap sec"><div class="g2"><div class="card box"><h2>Pide cita</h2><p>Ten a mano el modelo del equipo y una descripción de la avería o de la mejora que quieres hacer.</p><div class="btns"><a class="btn" href="{WA}">{ic("wa")}Pedir cita por WhatsApp</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}{TEL}</a></div></div>
<div class="card box"><h2>Cómo llegar</h2><p>{DIR}<br>Atención con cita previa.</p><a class="btn ghost" href="{MAPS}" rel="noopener">{ic("pin")}Abrir mapa</a></div>
<div class="card box"><h2>Correo</h2><p><a href="mailto:{MAIL}">{MAIL}</a></p></div></div></section>"""
    write("contacto.html", page("", "Contacto | VRPC", "Contacto y cita previa en VENTAREPARACIONPC, L'Hospitalet de Llobregat.", body, "contacto.html", extra_head=negocio_ld()))
    body = head_band([("index.html", "Inicio"), (None, "Ubicación")], "Ubicación") + f'<section class="wrap sec"><div class="card box"><p>{DIR}</p><p>Atención con cita previa. Teléfono: <a href="{TEL_LINK}">{TEL}</a></p><a class="btn" href="{MAPS}" rel="noopener">{ic("pin")}Abrir mapa</a></div></section>'
    write("ubicacion.html", page("", "Ubicación | VRPC", "Dónde está VentaReparacionPC: Carrer de les Aigües del Llobregat, 115, interior, 08906 L'Hospitalet de Llobregat. Atención con cita previa.", body, extra_head=negocio_ld()))
    # Textos legales: ver tools/legal.py (datos del titular en DATOS; lo que falte sale marcado como PENDIENTE)
    legal.PENDIENTES.clear()
    for slug, t, fn in (("aviso-legal", "Aviso legal", legal.aviso_legal), ("politica-de-cookies", "Política de cookies", legal.cookies)):
        body = head_band([("index.html", "Inicio"), (None, t)], t) + fn()
        write(f"{slug}.html", page("", f"{t} | VRPC", t, body))

    # ---- 404 (fuera de sitemap, sin canonical, noindex siempre, rutas resueltas via <base>)
    body = '<section class="band"><div class="wrap"><h1>Página no encontrada</h1><p>La dirección que buscas no existe o ha cambiado de ubicación.</p></div></section>' \
           '<section class="wrap sec"><div class="card box"><p>Puedes volver al inicio o ir directamente a las secciones principales del taller y de equipos PC Gaming.</p>' \
           '<div class="btns"><a class="btn" href="index.html">Ir al inicio</a><a class="btn ghost" href="servicios.html">Servicios</a><a class="btn ghost" href="pc-gaming.html">PC Gaming</a><a class="btn ghost" href="blog.html">Blog</a><a class="btn ghost" href="contacto.html">Contacto</a></div></div></section>'
    write("404.html", page("", "Página no encontrada | VRPC", "La página solicitada no existe en VentaReparacionPC.", body, is_404=True))

    # logo
    (ROOT / "assets").mkdir(exist_ok=True)
    write("assets/logo.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 42" width="140" height="42"><text x="0" y="29" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-style="italic" font-size="32" fill="#1d4fb8">VRPC</text><text x="1" y="40" font-family="Arial,sans-serif" font-weight="700" font-size="7.5" letter-spacing="1" fill="#0f2a5c">VENTAREPARACIONPC</text></svg>')
    # ---- redirecciones desde las URLs antiguas, sitemap y robots
    redirects = dict(REDIRECTS)
    for c in pcs:
        if c.get("old"):
            redirects[c["old"]] = f"pc/{c['slug']}.html"
    # variante "-a" que figuraba en el sitemap antiguo: misma configuración
    redirects.setdefault("ryzen-7-7800x3d-rtx5070-32-gb-1-tb-r.l.-a.html", "pc/ryzen-7-7800x3d-rtx5070-32-gb-1-tb-r-l.html")
    for old, new in redirects.items():
        write_redirect(old, new)
    legales = {"aviso-legal.html", "politica-de-cookies.html"} if legal.PENDIENTES else set()   # con datos pendientes: fuera del sitemap
    urls = "".join(f"<url><loc>{url_of(x)}</loc></url>\n" for x in SITEMAP if x not in legales)
    if legal.PENDIENTES:
        print("AVISO legal: faltan datos del titular en tools/legal.py ->", ", ".join(legal.PENDIENTES))
    if not RESENAS or not RES["fecha"] or not RES["escribir"]:
        print("AVISO reseñas: pendiente en build.py -> " + ", ".join(k for k, v in (("RESENAS (textos reales)", RESENAS), ("RES['fecha']", RES["fecha"]), ("RES['escribir']", RES["escribir"])) if not v))
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print("ok", len(pcs), "PCs ·", len(SITEMAP), "páginas ·", len(redirects), "redirecciones ·", "INDEXABLE" if INDEXAR else "noindex")

if __name__ == "__main__":
    build()
