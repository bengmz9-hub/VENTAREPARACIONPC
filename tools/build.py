#!/usr/bin/env python3
"""Genera el sitio estático (HTML) de VRPC en la raíz del repo.
Uso:  python tools/build.py
Lee las fichas de PC desde varios/sitio (solo local) la primera vez y deja
los datos en data/pcs.json; después ya no hace falta 'varios/'."""
import html, json, re, shutil, sys
from pathlib import Path

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
            pcs.append(dict(slug=re.sub(r"[^a-z0-9]+", "-", f.stem.lower()).strip("-"), title=title,
                            brand="Intel" if "intel" in f.stem.lower() else "AMD",
                            price=price, desc=desc, img=case))
        data.parent.mkdir(exist_ok=True)
        data.write_text(json.dumps(pcs, ensure_ascii=False, indent=1), encoding="utf-8")
    return json.loads(data.read_text(encoding="utf-8"))

# ------------------------------------------------------------------ contenido
SERVICES = [
    dict(slug="mantenimiento-pc-gaming", t="Mantenimiento PC Gaming", d="Limpieza interna, pasta térmica y revisión de la refrigeración.", img="Mantenimiento-PC-Gaming---6.webp", main=True, icon="fan",
         p=["Con el tiempo el polvo se acumula en filtros, ventiladores y disipadores, y el equipo sube de temperatura y hace más ruido. Hacemos una limpieza interna cuidadosa y revisamos la refrigeración.",
            "Cambiamos la pasta térmica cuando hace falta, revisamos ventiladores y flujo de aire y comprobamos temperaturas antes y después."],
         steps=["Limpieza interna de polvo (filtros, ventiladores, disipador)", "Revisión de la refrigeración y del flujo de aire", "Pasta térmica si procede", "Comprobación de temperaturas"],
         extra="Mantenimiento desde 70 €. Te damos el presupuesto antes de empezar."),
    dict(slug="actualizacion-pc-gaming", t="Actualización de PC Gaming", d="Amplía la RAM, instala un SSD o cambia la gráfica.", img="TECNICO-INFORMATICO---10--1-.webp", main=True, icon="chart",
         p=["Si tu PC ya no rinde como antes, a veces basta con cambiar una pieza. Te ayudamos a elegir qué actualizar primero según lo que usas y tu presupuesto.",
            "Comprobamos la compatibilidad con tu placa, fuente y caja antes de comprar nada."],
         steps=["Revisión del equipo y de lo que necesitas", "Propuesta de componentes compatibles", "Instalación y pruebas", "Comprobación final de rendimiento"],
         extra="Cuéntanos modelo y uso y te orientamos."),
    dict(slug="actualizacion-bios", t="Actualización de BIOS", d="Comprobación del firmware y de la compatibilidad de tu placa base.", img="Actulizacion-BIOS---2_800x800.webp", icon="wrench",
         p=["Una BIOS actualizada puede ser necesaria para admitir un procesador nuevo o corregir fallos. Es una operación delicada: la hacemos comprobando antes la versión y la compatibilidad de tu placa."], steps=["Identificación de placa y versión", "Comprobación de compatibilidad", "Actualización controlada", "Verificación de arranque"], extra=""),
    dict(slug="asistencia-remota", t="Asistencia remota", d="Ayuda a distancia para incidencias de software.", img="Asistencia-Remota---3_800x800.webp", icon="wrench",
         p=["Para problemas de software (sistema, programas, configuración) podemos ayudarte a distancia sin que tengas que traer el equipo."], steps=["Nos cuentas el problema", "Acordamos cita", "Conexión remota con tu permiso", "Resolución y comprobación"], extra=""),
    dict(slug="asesoramiento-compra", t="Asesoramiento de compra", d="Elige componentes compatibles con tu presupuesto.", img="ASESORAMIENTO-COMPRA-PC---8.webp", icon="wrench",
         p=["Antes de comprar piezas o un equipo, te ayudamos a elegir componentes compatibles entre sí y ajustados a tu presupuesto y a tus juegos o programas."], steps=["Presupuesto y uso", "Selección de componentes", "Comprobación de compatibilidad", "Opción de montaje en el taller"], extra=""),
    dict(slug="servicio-de-montaje", t="Servicio de montaje", d="Montaje y pruebas de los componentes de tu PC.", img="Montaje-PC-Gaming---9.webp", icon="wrench",
         p=["Montamos tu PC con los componentes que ya tienes o con los que elijas, gestionamos los cables y probamos el equipo antes de entregarlo."], steps=["Recepción de componentes", "Montaje y cableado", "Instalación y pruebas", "Entrega con cita previa"], extra=""),
    dict(slug="convertir-documentos", t="Conversión de documentos", d="Ayuda con archivos que necesitas abrir o cambiar de formato.", img="CONVERTIR-DOCUMENTOS---1.webp", icon="wrench",
         p=["Te ayudamos a abrir o convertir documentos y fotos entre formatos habituales (DOC, PDF, XLS, PPT, JPG, PNG…)."], steps=["Nos traes o envías el archivo", "Conversión al formato que necesitas", "Comprobación del resultado"], extra=""),
]
BLOG = [
    dict(slug="cuando-necesita-mantenimiento-tu-pc-gaming", cat="Mantenimiento", t="¿Cuándo necesita mantenimiento tu PC Gaming?", d="Tres señales que puedes observar mientras juegas y qué información llevar al taller.", img="Mantenimiento-PC-Gaming---6.webp",
         sections=[("Fíjate en los cambios", "El polvo visible en los filtros, los ventiladores que hacen más ruido de lo habitual y un equipo que se calienta más con el mismo juego son buenas razones para revisar la refrigeración."),
                   ("Compara en condiciones parecidas", "Anota qué juegos usabas, cuándo empezó el cambio y si pasa siempre o solo después de un rato. Si tienes mediciones de temperatura anteriores, compáralas con el mismo juego y ajustes similares. La temperatura ambiente también influye."),
                   ("¿Limpieza o diagnóstico?", "Una limpieza preventiva puede tener sentido si encuentras polvo acumulado y el equipo funciona bien. Si hay apagados, bloqueos o el ventilador deja de girar, describe el síntoma al pedir cita para que se pueda valorar la causa.")]),
    dict(slug="que-actualizar-primero-en-tu-pc-gaming", cat="Actualizaciones", t="¿Qué actualizar primero en tu PC Gaming?", d="Cómo decidir entre ampliar la RAM, instalar un SSD o cambiar la tarjeta gráfica.", img="Montaje-PC-Gaming---9.webp",
         sections=[("Empieza por el cuello de botella", "Observa qué falla: si tarda en cargar, un SSD puede ayudar; si va justo de memoria al abrir varias cosas, la RAM; si los fotogramas por segundo caen en juegos exigentes, suele ser la gráfica."),
                   ("Comprueba la compatibilidad", "Antes de comprar, revisa tu placa base, la fuente de alimentación y el espacio de la caja. Una pieza potente no sirve si no es compatible con el resto."),
                   ("Pide asesoramiento", "Si dudas, cuéntanos tu equipo y tu presupuesto y te orientamos sobre qué mejora compensa más.")]),
    dict(slug="que-significan-los-led-de-la-placa-base", cat="Diagnóstico", t="¿Qué significan los LED de la placa base?", d="Qué comprobar si una luz de diagnóstico se queda encendida al arrancar.", img="MSI-MAG-B860-TOMAHAWK-WIFI---2_800x800.webp",
         sections=[("Busca CPU, DRAM, VGA y BOOT", "Muchas placas tienen cuatro LED de diagnóstico que indican en qué fase se detiene el arranque: procesador, memoria, gráfica o dispositivo de arranque."),
                   ("Qué comprobar primero", "Reasienta la memoria y la gráfica, revisa los cables de alimentación y desconecta lo que no sea imprescindible. Consulta el manual de tu placa para el significado exacto."),
                   ("Cuándo traerlo al taller", "Si el LED sigue encendido tras las comprobaciones básicas, descríbenos qué luz es y qué pasa al arrancar para valorar la causa.")]),
]
NAV = [("index.html", "Inicio"), ("servicios.html", "Servicios"), ("trabajos-realizados.html", "Trabajos realizados"), ("opiniones.html", "Opiniones"), ("pc-gaming.html", "PC Gaming"), ("blog.html", "Blog"), ("contacto.html", "Contacto")]

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

# ------------------------------------------------------------------ plantilla
def page(path, title, desc, body, active="", depth=0, extra_head="", hero=False):
    p = "../" * depth
    nav = "".join(f'<a href="{p}{h}"{" class=\"on\" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    cta = f"""<section class="cta"><div class="wrap cta-in"><div><h2>¿Tu ordenador necesita revisión?</h2><p>Cuéntanos qué le ocurre y pide cita en L'Hospitalet.</p></div>
<div class="btns"><a class="btn white" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost-w" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div></div></section>"""
    foot = f"""<footer class="foot"><div class="wrap foot-in"><div><strong>VENTAREPARACIONPC</strong><br><span>L'Hospitalet de Llobregat · {TEL}</span></div>
<nav aria-label="Pie"><a href="{p}contacto.html">Contacto</a><a href="{p}ubicacion.html">Ubicación</a><a href="{p}blog.html">Blog</a><a href="{p}aviso-legal.html">Aviso legal</a><a href="{p}politica-de-cookies.html">Política de cookies</a></nav></div></footer>"""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="icon" href="{p}assets/logo.svg" type="image/svg+xml"><link rel="stylesheet" href="{p}assets/css/style.css">{extra_head}</head>
<body><a class="skip" href="#main">Saltar al contenido</a>
<header class="top"><div class="wrap top-in"><a class="brand" href="{p}index.html" aria-label="VRPC Ventareparacionpc, inicio"><img src="{p}assets/logo.svg" alt="VRPC Ventareparacionpc" width="140" height="42"></a>
<button class="burger" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav">☰</button>
<nav id="nav" class="nav" aria-label="Principal">{nav}<a class="btn small mob-only" href="{WA}">{ic("cal")}Pedir cita</a></nav>
<a class="btn small desk-only" href="{WA}">{ic("cal")}Pedir cita</a></div></header>
<main id="main">{body}</main>{cta}{foot}<script src="{p}assets/js/main.js"></script></body></html>"""

def head_band(crumbs, h1, sub=""):
    c = " <span>›</span> ".join(f'<a href="{h}">{t}</a>' if h else f"<span>{t}</span>" for h, t in crumbs)
    return f'<section class="band"><div class="wrap"><nav class="crumbs" aria-label="Migas">{c}</nav><h1>{h1}</h1>{f"<p>{sub}</p>" if sub else ""}</div></section>'

def svc_card(s, p=""):
    return f"""<a class="card svc" href="{p}servicio/{s['slug']}.html"><img src="{p}{asset_img(s['img'])}" alt="" loading="lazy"><div class="svc-t">{ic(s['icon'])}<h3>{s['t']}</h3><p>{s['d']}</p><span class="more">Más información {ic("arrow")}</span></div></a>"""

def write(path, content):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")

def build():
    IMG.mkdir(parents=True, exist_ok=True)
    pcs = load_pcs()
    hero = asset_img("PC-INTEL-A-MEDIDA---8.webp")
    main_s = [s for s in SERVICES if s.get("main")]
    other_s = [s for s in SERVICES if not s.get("main")]

    # ---- Inicio
    steps = [("pc", "Traes tu equipo", "Nos cuentas qué le pasa a tu ordenador."), ("search", "Revisión delante de ti", "Comprobamos el equipo contigo."), ("chat", "Explicación clara", "Te contamos qué vemos y qué opciones tienes."), ("doc", "Presupuesto", "Valoramos el coste antes de empezar el trabajo.")]
    st = "".join(f'<li><span class="n">{i+1}</span>{ic(ic_)}<strong>{a}</strong><small>{b}</small></li>' for i, (ic_, a, b) in enumerate(steps))
    body = f"""<section class="hero"><div class="wrap hero-in"><div class="hero-t"><p class="kicker">Servicio técnico en L'Hospitalet de Llobregat</p>
<h1>Mantenimiento y actualizaciones de <em>PC Gaming</em></h1><p class="lead">Revisamos la refrigeración y el estado de tu PC. Si quieres mejorar su rendimiento, te ayudamos a elegir qué componentes actualizar.</p>
<div class="btns"><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div>
<ul class="ticks"><li>{ic("shield")}Revisión delante de ti</li><li>{ic("doc")}Presupuesto previo</li><li>{ic("star")}<a href="opiniones.html">Reseñas en Google</a></li></ul></div>
<div class="hero-img"><img src="{hero}" alt="PC gaming montado a medida en el taller" width="800" height="800"></div></div></section>
<section class="wrap home-grid"><div class="col-l"><div class="card steps"><p class="kicker c">Así trabajamos</p><h2>Servicio técnico transparente</h2><ol>{st}</ol></div>
<div class="ba"><div class="sec-h"><h2>Antes y después</h2><a href="trabajos-realizados.html">Ver trabajo completo {ic("arrow")}</a></div>
<div class="ba-g"><figure class="card"><img src="assets/img/antes.jpg" alt="Interior del PC con polvo acumulado" loading="lazy"><figcaption>{ic("alert","r")}Antes del mantenimiento</figcaption></figure>
<figure class="card"><img src="assets/img/despues.jpg" alt="Interior del PC limpio" loading="lazy"><figcaption>{ic("check","g")}Después del mantenimiento</figcaption></figure></div>
<p class="muted">Limpieza del interior de un PC Gaming con polvo acumulado.</p></div></div>
<div class="col-r"><div class="sec-h"><h2>Nuestros servicios</h2><a href="servicios.html">Ver todos los servicios {ic("arrow")}</a></div><div class="g2">{"".join(svc_card(s) for s in main_s)}</div>
<h2 class="sp">Lo que opinan nuestros clientes</h2><div class="card rev"><div class="rev-i">{ic("star")}</div><div><h3>VENTAREPARACIONPC en Google</h3><p>Consulta las valoraciones en nuestra ficha de L'Hospitalet.</p><a class="more" href="opiniones.html">Ver reseñas en Google {ic("arrow")}</a></div></div>
<div class="card rev"><div class="rev-i">{ic("pc")}</div><div><h3>PC Gaming a medida</h3><p>Equipos AMD e Intel montados bajo pedido.</p><a class="more" href="pc-gaming.html">Ver equipos {ic("arrow")}</a></div></div></div></section>"""
    write("index.html", page("index.html", "VRPC · Reparación y PC Gaming en L'Hospitalet", "Servicio técnico, mantenimiento y PC Gaming a medida en L'Hospitalet de Llobregat. Pide cita previa.", body, "index.html"))

    # ---- Servicios + fichas
    body = head_band([("index.html", "Inicio"), (None, "Servicio técnico")], "Servicio técnico", "Mantenimiento y mejoras de hardware para PC Gaming en L'Hospitalet de Llobregat.") + \
        f'<section class="wrap sec"><div class="g2 big">{"".join(svc_card(s) for s in main_s)}</div><h2 class="sp">Otros servicios</h2><div class="g3">{"".join(svc_card(s) for s in other_s)}</div></section>'
    write("servicios.html", page("servicios.html", "Servicio técnico | VRPC", "Servicios de mantenimiento, actualización, BIOS, asistencia remota y montaje de PC en L'Hospitalet.", body, "servicios.html"))
    for s in SERVICES:
        li = "".join(f"<li>{x}</li>" for x in s["steps"])
        body = head_band([("../index.html", "Inicio"), ("../servicios.html", "Servicios"), (None, s["t"])], s["t"], s["d"]) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover" src="../{asset_img(s['img'])}" alt="" loading="lazy">{"".join(f"<p>{x}</p>" for x in s['p'])}<h2>Qué incluye</h2><ul class="list">{li}</ul>{f'<p><strong>{s["extra"]}</strong></p>' if s['extra'] else ''}</article>
<aside class="card side"><h3>Pide cita</h3><p>Cuéntanos el modelo y lo que necesitas. Atendemos con cita previa en L'Hospitalet.</p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></aside></section>"""
        write(f"servicio/{s['slug']}.html", page("", f"{s['t']} | VRPC", s["d"], body, "servicios.html", 1))

    # ---- Trabajos realizados
    body = head_band([("index.html", "Inicio"), (None, "Trabajos realizados")], "Trabajos realizados") + f"""<section class="wrap sec two"><div><h2>Limpieza interna de un PC Gaming</h2>
<div class="ba-g"><figure class="card"><img src="assets/img/antes.jpg" alt="Interior del PC con polvo acumulado" loading="lazy" data-zoom><figcaption>{ic("alert","r")}Antes del mantenimiento{ic("zoom","z")}</figcaption></figure>
<figure class="card"><img src="assets/img/despues.jpg" alt="Interior del PC limpio" loading="lazy" data-zoom><figcaption>{ic("check","g")}Después del mantenimiento{ic("zoom","z")}</figcaption></figure></div>
<p class="muted">Las fotos muestran el interior del equipo antes y después de retirar el polvo acumulado. Pulsa en cualquiera para ampliarla.</p></div>
<aside><div class="card side"><h3>Pide cita para tu equipo</h3><p>Cuéntanos el modelo y lo que necesitas. Atendemos con cita previa en L'Hospitalet.</p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></div>
<div class="card side"><h3>Servicio de este trabajo</h3><a class="more row" href="servicio/mantenimiento-pc-gaming.html">Mantenimiento PC Gaming {ic("arrow")}</a></div></aside></section>"""
    write("trabajos-realizados.html", page("", "Trabajos realizados | VRPC", "Ejemplos de trabajos realizados en el taller: antes y después de una limpieza interna de PC Gaming.", body, "trabajos-realizados.html"))

    # ---- Opiniones
    body = head_band([("index.html", "Inicio"), (None, "Opiniones de clientes")], "Opiniones de clientes", "Lee en Google las experiencias que han compartido quienes han pasado por el taller.") + f"""<section class="wrap sec two"><div class="card rev big"><div class="rev-i">{ic("star")}</div><div><h3>VENTAREPARACIONPC en Google</h3><p>Consulta las valoraciones en nuestra ficha de L'Hospitalet.</p><a class="more" href="{MAPS}" rel="noopener">Abrir ficha de Google Maps {ic("arrow")}</a></div></div>
<aside class="card side"><h3>Conoce el taller</h3><a class="more row" href="trabajos-realizados.html">Trabajos realizados {ic("arrow")}</a><a class="more row" href="ubicacion.html">Ubicación {ic("arrow")}</a><a class="more row" href="contacto.html">Contacto {ic("arrow")}</a></aside></section>"""
    write("opiniones.html", page("", "Opiniones de clientes | VRPC", "Opiniones de clientes de VENTAREPARACIONPC en Google.", body, "opiniones.html"))

    # ---- PC Gaming
    cards = "".join(f"""<a class="card pc" href="pc/{c['slug']}.html" data-brand="{c['brand']}" data-t="{E(c['title'].lower())}"><img src="{asset_img(c['img'])}" alt="" loading="lazy"><div class="pc-b"><span class="brand-tag {c['brand'].lower()}">{c['brand'].upper() if c['brand']=='Intel' else 'AMD'}</span><h3>{E(c['title'])}</h3><span class="more">Ver ficha {ic("arrow")}</span></div></a>""" for c in pcs)
    body = head_band([("index.html", "Inicio"), (None, "PC Gaming a medida")], "PC Gaming a medida", "Explora las configuraciones AMD e Intel de VRPC. Montamos los equipos bajo pedido.") + f"""<section class="wrap sec"><div class="filters" id="filters"><button class="chip on" data-f="all">Todos</button><button class="chip" data-f="AMD">AMD Ryzen</button><button class="chip" data-f="Intel">Intel</button></div>
<div class="searchrow"><label for="q">Buscar</label><div><input id="q" type="search" placeholder="Por ejemplo, Ryzen 7 o RTX 5070"><span id="count" aria-live="polite">{len(pcs)} resultados</span></div></div>
<div class="g4" id="grid">{cards}</div></section>"""
    write("pc-gaming.html", page("", "PC Gaming a medida | VRPC", "Configuraciones de PC Gaming AMD Ryzen e Intel montadas bajo pedido en L'Hospitalet.", body, "pc-gaming.html"))
    for c in pcs:
        specs = [x.strip() for x in re.split(r"\.\s+", c["desc"]) if x.strip()]
        body = head_band([("../index.html", "Inicio"), ("../pc-gaming.html", "PC Gaming"), (None, E(c["title"]))], E(c["title"])) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover contain" src="../{asset_img(c['img'])}" alt="Caja del equipo {E(c['title'])}">
<p class="price">{c['price']} € <small>precio sin descuento</small></p><ul class="list">{"".join(f"<li>{E(x.rstrip('.'))}</li>" for x in specs)}</ul>
<ul class="list"><li>Montaje bajo pedido</li><li>Windows 11 Pro licencia oficial (según configuración)</li></ul><p class="muted">Precios de referencia (última actualización conocida: 31-07-26). Confirma disponibilidad y plazo de entrega al pedir cita.</p></article>
<aside class="card side"><h3>Pide cita para este equipo</h3><p>Te confirmamos precio, plazo de entrega y posibles cambios de componentes.</p><a class="btn" href="{WA}?text={E(c['title'].replace(' ','%20'))}">{ic("wa")}Consultar por WhatsApp</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}Llamar ahora</a></aside></section>"""
        write(f"pc/{c['slug']}.html", page("", f"{c['title']} | PC Gaming VRPC", c["desc"][:155], body, "pc-gaming.html", 1))

    # ---- Blog
    bc = "".join(f"""<a class="card post" href="blog/{b['slug']}.html"><img src="{asset_img(b['img'])}" alt="" loading="lazy"><div class="pc-b"><span class="cat">{b['cat']}</span><h3>{b['t']}</h3><p>{b['d']}</p></div></a>""" for b in BLOG)
    body = head_band([("index.html", "Inicio"), (None, "Blog")], "Blog", "Guías de VRPC para cuidar, mejorar y entender tu PC Gaming.") + f'<section class="wrap sec"><div class="g3">{bc}</div></section>'
    write("blog.html", page("", "Blog | VRPC", "Guías para cuidar, mejorar y entender tu PC Gaming.", body, "blog.html"))
    for b in BLOG:
        more = "".join(f'<a class="more row" href="{o["slug"]}.html">{o["t"]} {ic("arrow")}</a>' for o in BLOG if o is not b)
        secs = "".join(f"<h2>{h}</h2><p>{t}</p>" for h, t in b["sections"])
        body = head_band([("../index.html", "Inicio"), ("../blog.html", "Blog"), (None, b["cat"])], b["t"], b["d"]) + f"""<section class="wrap sec two"><article class="card prose"><img class="cover" src="../{asset_img(b['img'])}" alt="" loading="lazy">{secs}<p><a class="btn" href="{WA}">{ic("cal")}Solicitar cita previa</a></p></article><aside class="card side"><h3>Más guías</h3>{more}</aside></section>"""
        write(f"blog/{b['slug']}.html", page("", f"{b['t']} | Blog VRPC", b["d"], body, "blog.html", 1))

    # ---- Contacto / ubicación / legales
    body = head_band([("index.html", "Inicio"), (None, "Contacto")], "Contacto", "Contacta con VRPC para concertar una cita antes de traer tu ordenador.") + f"""<section class="wrap sec"><div class="g2"><div class="card box"><h2>Pide cita</h2><p>Ten a mano el modelo del equipo y una descripción de la avería o de la mejora que quieres hacer.</p><div class="btns"><a class="btn" href="{WA}">{ic("wa")}Pedir cita por WhatsApp</a><a class="btn ghost" href="{TEL_LINK}">{ic("phone")}{TEL}</a></div></div>
<div class="card box"><h2>Cómo llegar</h2><p>{DIR}<br>Atención con cita previa.</p><a class="btn ghost" href="{MAPS}" rel="noopener">{ic("pin")}Abrir mapa</a></div>
<div class="card box"><h2>Correo</h2><p><a href="mailto:{MAIL}">{MAIL}</a></p></div></div></section>"""
    write("contacto.html", page("", "Contacto | VRPC", "Contacto y cita previa en VENTAREPARACIONPC, L'Hospitalet de Llobregat.", body, "contacto.html"))
    body = head_band([("index.html", "Inicio"), (None, "Ubicación")], "Ubicación") + f'<section class="wrap sec"><div class="card box"><p>{DIR}</p><p>Atención con cita previa. Teléfono: <a href="{TEL_LINK}">{TEL}</a></p><a class="btn" href="{MAPS}" rel="noopener">{ic("pin")}Abrir mapa</a></div></section>'
    write("ubicacion.html", page("", "Ubicación | VRPC", "Dónde estamos: L'Hospitalet de Llobregat.", body))
    for slug, t in (("aviso-legal", "Aviso legal"), ("politica-de-cookies", "Política de cookies")):
        body = head_band([("index.html", "Inicio"), (None, t)], t) + '<section class="wrap sec"><div class="card box"><p>Texto pendiente de completar con los datos del titular. (Aquí se migrará el texto legal de la web actual.)</p></div></section>'
        write(f"{slug}.html", page("", f"{t} | VRPC", t, body))

    # logo
    (ROOT / "assets").mkdir(exist_ok=True)
    write("assets/logo.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 42" width="140" height="42"><text x="0" y="29" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-style="italic" font-size="32" fill="#1d4fb8">VRPC</text><text x="1" y="40" font-family="Arial,sans-serif" font-weight="700" font-size="7.5" letter-spacing="1" fill="#0f2a5c">VENTAREPARACIONPC</text></svg>')
    print("ok", len(pcs), "PCs")

if __name__ == "__main__":
    build()
