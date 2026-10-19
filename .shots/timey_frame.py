#!/usr/bin/env python3
"""Timey mockups — same phone frame as Nabtat / Spicy, warm charcoal + gold canvas."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

SRC_DIR = "/Users/mohamedayman/Development/portfolio/.shots/timey-src"
DST_DIR = "/Users/mohamedayman/Development/portfolio/assets"

CANVAS_W, CANVAS_H = 473, 1024
SCALE = 2

BG_TOP = (22, 18, 14)
BG_BOT = (46, 36, 26)
GLOW = (196, 164, 124)
BEZEL = (14, 14, 16)
BEZEL_EDGE = (56, 50, 42)


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
    for i, alpha in enumerate((38, 22, 12, 6)):
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


def is_dark(pixel, thresh=38):
    if isinstance(pixel, int):
        return pixel < thresh
    return pixel[0] + pixel[1] + pixel[2] < thresh * 3


def crop_letterbox(im):
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    step = 3

    def col_content(x):
        dark = tot = 0
        for y in range(0, h, step):
            tot += 1
            if is_dark(px[x, y]):
                dark += 1
        return dark / tot < 0.88

    def row_content(y):
        dark = tot = 0
        for x in range(0, w, step):
            tot += 1
            if is_dark(px[x, y]):
                dark += 1
        return dark / tot < 0.88

    left = 0
    while left < w - 2 and not col_content(left):
        left += 1
    right = w - 1
    while right > left and not col_content(right):
        right -= 1
    top = 0
    while top < h - 2 and not row_content(top):
        top += 1
    bottom = h - 1
    while bottom > top and not row_content(bottom):
        bottom -= 1

    pad = 1
    box = (
        max(0, left + pad),
        max(0, top + pad),
        min(w, right - pad + 1),
        min(h, bottom - pad + 1),
    )
    cw, ch = box[2] - box[0], box[3] - box[1]
    if cw < 80 or ch < 120:
        return im
    return rgb.crop(box)


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


def mockup(shot, letterbox=False):
    shot = shot.convert("RGB")
    if letterbox:
        shot = crop_letterbox(shot)
    else:
        shot = crop_android_chrome(shot)
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

    btn_c = (38, 36, 32, 255)
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
    ("timey-1-stories.png", "timey-1-stories.jpg"),
    ("timey-2-chat.png", "timey-2-chat.jpg"),
    ("timey-3-camera.png", "timey-3-camera.jpg"),
    ("timey-4-profile.png", "timey-4-profile.jpg"),
    ("timey-5-trending.png", "timey-5-trending.jpg"),
    ("timey-6-tips.png", "timey-6-tips.jpg"),
    ("timey-7-call.png", "timey-7-call.jpg", True),
    ("timey-8-splash.png", "timey-8-splash.jpg"),
]


def main():
    for job in JOBS:
        src_name, dst_name = job[0], job[1]
        letterbox = job[2] if len(job) > 2 else False
        im = Image.open(os.path.join(SRC_DIR, src_name))
        out = mockup(im, letterbox=letterbox)
        dest = os.path.join(DST_DIR, dst_name)
        out.save(dest, "JPEG", quality=86, optimize=True, progressive=True)
        print(f"{dst_name}: {out.size}  {os.path.getsize(dest)} bytes")


if __name__ == "__main__":
    main()
