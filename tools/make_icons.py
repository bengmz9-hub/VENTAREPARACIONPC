#!/usr/bin/env python3
"""Genera los iconos PNG/ICO de VRPC a partir de la marca (#1d5fd1 y texto blanco VRPC).
Uso manual (no se ejecuta desde build.py): python tools/make_icons.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BG = (29, 95, 209)
FG = (255, 255, 255)
TEXT = "VRPC"
SIZE = 1024

FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\ariblk.ttf"),
    Path(r"C:\Windows\Fonts\arialbd.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]


def pick_font(target_w: int, target_h: int):
    font_path = next((p for p in FONT_CANDIDATES if p.exists()), None)
    if not font_path:
        return ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGBA", (SIZE, SIZE)))
    for sz in range(420, 40, -2):
        font = ImageFont.truetype(str(font_path), sz)
        bbox = probe.textbbox((0, 0), TEXT, font=font)
        if (bbox[2] - bbox[0]) <= target_w and (bbox[3] - bbox[1]) <= target_h:
            return font
    return ImageFont.truetype(str(font_path), 40)


def render_icon(rounded: bool) -> Image.Image:
    mode = "RGBA" if rounded else "RGB"
    bg = (0, 0, 0, 0) if rounded else BG
    img = Image.new(mode, (SIZE, SIZE), bg)
    draw = ImageDraw.Draw(img)
    if rounded:
        draw.rounded_rectangle([(0, 0), (SIZE - 1, SIZE - 1)], radius=round(SIZE * 0.22), fill=BG + (255,))
    font = pick_font(int(SIZE * 0.80), int(SIZE * 0.50))
    bbox = draw.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (SIZE - tw) / 2 - bbox[0]
    y = (SIZE - th) / 2 - bbox[1]
    draw.text((x, y), TEXT, font=font, fill=FG + (255,) if rounded else FG)
    return img


def main():
    icons_dir = ROOT / "docs" / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    master_rgba = render_icon(rounded=True)
    master_rgb = render_icon(rounded=False)

    p512 = icons_dir / "icon-512.png"
    master_rgba.resize((512, 512), Image.Resampling.LANCZOS).save(p512, format="PNG", optimize=True)

    p192 = icons_dir / "icon-192.png"
    master_rgba.resize((192, 192), Image.Resampling.LANCZOS).save(p192, format="PNG", optimize=True)

    pico = ROOT / "docs" / "favicon.ico"
    master_rgba.save(pico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])

    papple = ROOT / "docs" / "apple-touch-icon.png"
    master_rgb.resize((180, 180), Image.Resampling.LANCZOS).save(papple, format="PNG", optimize=True)

    for p in (pico, papple, p192, p512):
        print(f"ok {p.relative_to(ROOT).as_posix()} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
