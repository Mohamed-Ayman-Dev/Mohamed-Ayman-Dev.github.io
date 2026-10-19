#!/usr/bin/env python3
"""Nabtat Hasana mockups — same phone frame as Timey, forest-green canvas."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

SRC_DIR = "/Users/mohamedayman/Development/portfolio/.shots/nabtat-src"
DST_DIR = "/Users/mohamedayman/Development/portfolio/assets"

CANVAS_W, CANVAS_H = 473, 1024
SCALE = 2

BG_TOP = (10, 28, 20)
BG_BOT = (26, 74, 50)
GLOW = (168, 196, 92)
BEZEL = (14, 14, 16)
BEZEL_EDGE = (48, 56, 50)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_background(w, h):
    img = Image.new("RGB", (w, h), BG_TOP)
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(h):
        t = y / max(h - 1, 1)
        t = t * t * (3 - 2 * t)
        c = lerp(BG_TOP, BG_BOT, t)
        draw.line([(0, y), (w, y)], fill=c)

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = w // 2, int(h * 0.50)
    for i, alpha in enumerate((30, 18, 10, 5)):
        r = int(w * (0.62 - i * 0.08))
        ry = int(r * 1.15)
        gdraw.ellipse(
            [cx - r, cy - ry, cx + r, cy + ry],
            fill=(GLOW[0], GLOW[1], GLOW[2], alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    rings = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    for i in range(3):
        r = int(w * (0.38 + i * 0.22))
        rd.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(GLOW[0], GLOW[1], GLOW[2], 18 - i * 4),
            width=2,
        )
    rings = rings.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img.convert("RGBA"), rings).convert("RGB")
    return img


def crop_android_chrome(im, top=42, bottom=22):
    """Strip status bar + gesture line only — keep the app header intact."""
    w, h = im.size
    return im.crop((0, top, w, h - bottom))


def round_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def contain_resize(im, size, fill=(8, 8, 10)):
    tw, th = size
    iw, ih = im.size
    scale = min(tw / iw, th / ih)
    nw, nh = max(1, int(iw * scale + 0.5)), max(1, int(ih * scale + 0.5))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, fill)
    canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def edge_fill(im):
    """Use the shot's top pixels so letterbox matches the app, not a black gap."""
    band = im.crop((0, 0, im.size[0], min(12, im.size[1]))).resize((1, 1), Image.Resampling.BOX)
    return band.getpixel((0, 0))


def mockup(shot):
    shot = crop_android_chrome(shot.convert("RGB"))
    fill = edge_fill(shot)

    sw, sh = CANVAS_W * SCALE, CANVAS_H * SCALE
    canvas = make_background(sw, sh)

    shot_aspect = shot.size[0] / shot.size[1]
    phone_h = int(sh * 0.86)
    bezel = max(22, int(phone_h * 0.022))
    island_h = max(20, int(bezel * 1.05))
    home_h = max(8, int(bezel * 0.38))
    inner_r = 40
    top_safe = island_h + 14
    bot_safe = home_h + 18
    screen_h = phone_h - 2 * bezel
    content_h = screen_h - top_safe - bot_safe
    screen_w = int(content_h * shot_aspect)
    phone_w = screen_w + 2 * bezel
    outer_r = max(inner_r + bezel - 4, int(phone_w * 0.10))
    px = (sw - phone_w) // 2
    py = (sh - phone_h) // 2 + int(sh * 0.008)

    shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [px + 8, py + 28, px + phone_w + 8, py + phone_h + 28],
        radius=outer_r,
        fill=(0, 0, 0, 160),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow)

    phone = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone)
    pd.rounded_rectangle(
        [px, py, px + phone_w, py + phone_h],
        radius=outer_r,
        fill=BEZEL + (255,),
    )
    pd.rounded_rectangle(
        [px + 2, py + 2, px + phone_w - 2, py + phone_h - 2],
        radius=outer_r - 2,
        outline=BEZEL_EDGE + (255,),
        width=2,
    )

    btn_c = (38, 36, 42, 255)
    pd.rounded_rectangle([px - 5, py + int(phone_h * 0.16), px + 2, py + int(phone_h * 0.20)], 3, fill=btn_c)
    pd.rounded_rectangle([px - 6, py + int(phone_h * 0.24), px + 2, py + int(phone_h * 0.34)], 3, fill=btn_c)
    pd.rounded_rectangle([px - 6, py + int(phone_h * 0.36), px + 2, py + int(phone_h * 0.46)], 3, fill=btn_c)
    pd.rounded_rectangle(
        [px + phone_w - 2, py + int(phone_h * 0.28), px + phone_w + 6, py + int(phone_h * 0.42)],
        3,
        fill=btn_c,
    )

    canvas = Image.alpha_composite(canvas, phone)

    sx0 = px + bezel
    sy0 = py + bezel
    sx1 = px + phone_w - bezel
    sy1 = py + phone_h - bezel
    screen_w, screen_h = sx1 - sx0, sy1 - sy0

    screen_bg = Image.new("RGB", (screen_w, screen_h), fill)
    content = contain_resize(shot, (screen_w, content_h), fill=fill)
    content = ImageEnhance.Contrast(content).enhance(1.03)
    content = ImageEnhance.Color(content).enhance(1.04)
    content = content.filter(ImageFilter.UnsharpMask(radius=1.1, percent=70, threshold=2))
    screen_bg.paste(content, (0, top_safe))

    mask = round_mask((screen_w, screen_h), inner_r)
    screen_rgba = screen_bg.convert("RGBA")
    screen_rgba.putalpha(mask)
    canvas.paste(screen_rgba, (sx0, sy0), screen_rgba)

    island_w = int(screen_w * 0.30)
    ix0 = sx0 + (screen_w - island_w) // 2
    iy0 = sy0 + int((top_safe - island_h) / 2)
    idraw = ImageDraw.Draw(canvas)
    idraw.rounded_rectangle(
        [ix0, iy0, ix0 + island_w, iy0 + island_h],
        radius=island_h // 2,
        fill=(8, 8, 10, 255),
    )
    dot = max(6, island_h // 3)
    idraw.ellipse(
        [ix0 + island_w - island_h - 4, iy0 + (island_h - dot) // 2,
         ix0 + island_w - island_h - 4 + dot, iy0 + (island_h - dot) // 2 + dot],
        fill=(22, 40, 32, 255),
    )

    hw = int(screen_w * 0.28)
    hh = home_h
    hx0 = sx0 + (screen_w - hw) // 2
    hy0 = sy1 - int((bot_safe + hh) / 2)
    idraw.rounded_rectangle(
        [hx0, hy0, hx0 + hw, hy0 + hh],
        radius=hh // 2,
        fill=(255, 255, 255, 70),
    )

    return canvas.convert("RGB").resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)


JOBS = [
    ("nabtat-1-splash.png", "nabtat-1-splash.jpg"),
    ("nabtat-2-home.png", "nabtat-2-home.jpg"),
    ("nabtat-3-categories.png", "nabtat-3-categories.jpg"),
    ("nabtat-4-listing.png", "nabtat-4-listing.jpg"),
    ("nabtat-5-product.png", "nabtat-5-product.jpg"),
    ("nabtat-6-cart.png", "nabtat-6-cart.jpg"),
]


def main():
    for src_name, dst_name in JOBS:
        im = Image.open(os.path.join(SRC_DIR, src_name))
        out = mockup(im)
        dest = os.path.join(DST_DIR, dst_name)
        out.save(dest, "JPEG", quality=86, optimize=True, progressive=True)
        print(f"{dst_name}: {out.size}  {os.path.getsize(dest)} bytes")


if __name__ == "__main__":
    main()
