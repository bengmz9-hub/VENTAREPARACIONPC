"""Optimiza las imágenes de la portada (ejecutar antes de build.py; es idempotente).

1. Convierte a webp las imágenes que sigan en jpg/png (antes.jpg, despues.jpg).
2. Genera versiones reducidas (-w320, -w640, -w480...) de las imágenes que la portada
   muestra a un tamaño mucho menor que el original, para usarlas con srcset.
Usa solo Pillow. No toca los originales webp.
"""
import re
from pathlib import Path
from PIL import Image

IMG = Path(__file__).resolve().parent.parent / "docs" / "assets" / "img"
Q = 78

# imágenes grandes que ninguna página usa (no se generan variantes)
SIN_USO = {"ANTEC-C8---1.webp"}

# imagen -> anchos de las versiones reducidas
VARIANTES = {
    "CAJA-ARGB-7-VENT.---11.webp": (480, 800),                     # hero
    "TECNICO-INFORMATICO---10--1-.webp": (320, 640),
    "Mantenimiento-PC-Gaming---6.webp": (320, 640),
    "Montaje-PC-Gaming---9.webp": (320, 640),
    "Asistencia-Remota---3_800x800.webp": (320, 640),
    "ASESORAMIENTO-COMPRA-PC---8.webp": (320, 640),
    "MSI-MAG-B860-TOMAHAWK-WIFI---2_800x800.webp": (320, 640),
    "CAJA-NZXT-H9-Flow---2.webp": (320, 640),
    "PC-INTEL-A-MEDIDA---8.webp": (320, 640),
}


def a_webp():
    for src in sorted(IMG.glob("*.jpg")) + sorted(IMG.glob("*.png")):
        dst = src.with_suffix(".webp")
        if dst.exists():
            continue
        Image.open(src).convert("RGB").save(dst, "WEBP", quality=Q, method=6)
        print(f"webp  {src.name} {src.stat().st_size} B -> {dst.name} {dst.stat().st_size} B")


def objetivos():
    """Los de VARIANTES con sus anchos y, además, cualquier webp de 700 px o más (tarjetas de servicios,
    portadas de las fichas de PC) con las versiones estándar de 320 y 640 px."""
    res = dict(VARIANTES)
    for src in sorted(IMG.glob("*.webp")):
        if re.search(r"-w\d+\.webp$", src.name) or src.name in res or src.name in SIN_USO:
            continue
        if Image.open(src).width >= 700:
            res[src.name] = (320, 640)
    return res


def variantes():
    for nombre, anchos in objetivos().items():
        src = IMG / nombre
        if not src.exists():
            print("FALTA", nombre)
            continue
        im = Image.open(src)
        for w in anchos:
            if w >= im.width:
                continue
            dst = IMG / f"{src.stem}-w{w}.webp"
            if dst.exists():
                continue
            h = round(im.height * w / im.width)
            im.convert("RGB" if im.mode not in ("RGB", "RGBA") else im.mode).resize((w, h), Image.LANCZOS).save(dst, "WEBP", quality=Q, method=6)
            print(f"w{w}   {dst.name} {dst.stat().st_size} B")


if __name__ == "__main__":
    a_webp()
    variantes()
