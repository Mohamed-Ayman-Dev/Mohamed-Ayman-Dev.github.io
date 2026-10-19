#!/usr/bin/env python3
"""First Timey mockup look — 473x1024, dark purple, slim black phone."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

SRC_DIR = "/Users/mohamedayman/.cursor/projects/Users-mohamedayman-Development-portfolio/assets"
DST_DIR = "/Users/mohamedayman/Development/portfolio/assets"

CANVAS_W, CANVAS_H = 473, 1024
SCALE = 2

BG_TOP = (16, 10, 36)
BG_BOT = (42, 24, 80)
GOLD = (196, 164, 124)
BEZEL = (14, 14, 16)
BEZEL_EDGE = (52, 48, 58)


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
    for i, alpha in enumerate((28, 18, 10, 5)):
        r = int(w * (0.62 - i * 0.08))
        ry = int(r * 1.15)
        gdraw.ellipse(
            [cx - r, cy - ry, cx + r, cy + ry],
            fill=(GOLD[0], GOLD[1], GOLD[2], alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(42))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    rings = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    for i in range(3):
        r = int(w * (0.38 + i * 0.22))
        rd.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(GOLD[0], GOLD[1], GOLD[2], 18 - i * 4),
            width=2,
        )
    rings = rings.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.alpha_composite(img.convert("RGBA"), rings).convert("RGB")
    return img


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


def crop_status(im, top_frac=0.037, bottom_frac=0.0):
    w, h = im.size
    top = int(round(h * top_frac))
    bot = int(round(h * bottom_frac))
    return im.crop((0, top, w, h - bot if bot else h))


def round_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def cover_resize(im, size):
    tw, th = size
    iw, ih = im.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def mockup(shot, letterbox=False, crop_bottom=False):
    shot = shot.convert("RGB")
    if letterbox:
        shot = crop_letterbox(shot)
    else:
        shot = crop_status(shot, top_frac=0.037, bottom_frac=0.017 if crop_bottom else 0.0)

    sw, sh = CANVAS_W * SCALE, CANVAS_H * SCALE
    canvas = make_background(sw, sh)

    # Same first look, slightly wider — iPhone 19.5:9, not the skinny 0.43 body.
    phone_h = int(sh * 0.84)
    phone_w = int(phone_h * 9 / 19.5)
    px = (sw - phone_w) // 2
    py = (sh - phone_h) // 2 + int(sh * 0.01)

    bezel = max(14, int(phone_w * 0.038))
    outer_r = int(phone_w * 0.14)
    inner_r = max(18, outer_r - bezel + 2)

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
    sy0 = py + bezel + int(bezel * 0.15)
    sx1 = px + phone_w - bezel
    sy1 = py + phone_h - bezel
    screen_w, screen_h = sx1 - sx0, sy1 - sy0

    screen = cover_resize(shot, (screen_w, screen_h))
    screen = ImageEnhance.Contrast(screen).enhance(1.04)
    screen = ImageEnhance.Color(screen).enhance(1.05)
    screen = screen.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))

    mask = round_mask((screen_w, screen_h), inner_r)
    screen_rgba = screen.convert("RGBA")
    screen_rgba.putalpha(mask)
    canvas.paste(screen_rgba, (sx0, sy0), screen_rgba)

    island_w = int(screen_w * 0.32)
    island_h = max(16, int(bezel * 1.05))
    ix0 = sx0 + (screen_w - island_w) // 2
    iy0 = sy0 + int(bezel * 0.35)
    idraw = ImageDraw.Draw(canvas)
    idraw.rounded_rectangle(
        [ix0, iy0, ix0 + island_w, iy0 + island_h],
        radius=island_h // 2,
        fill=(8, 8, 10, 255),
    )
    dot = island_h // 3
    idraw.ellipse(
        [ix0 + island_w - island_h - 4, iy0 + (island_h - dot) // 2,
         ix0 + island_w - island_h - 4 + dot, iy0 + (island_h - dot) // 2 + dot],
        fill=(22, 28, 48, 255),
    )

    hw = int(screen_w * 0.28)
    hh = max(5, int(bezel * 0.28))
    hx0 = sx0 + (screen_w - hw) // 2
    hy0 = sy1 - int(bezel * 0.85)
    idraw.rounded_rectangle(
        [hx0, hy0, hx0 + hw, hy0 + hh],
        radius=hh // 2,
        fill=(255, 255, 255, 70),
    )

    out = canvas.convert("RGB").resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)
    return out


JOBS = [
    {"src": "image-85a03293-762f-4b65-a8ef-0889e5cb430d.png", "dst": "timey-1-stories.jpg"},
    {"src": "image-88870dfe-8c36-4e9d-8263-36e66c56fc14.png", "dst": "timey-2-chat.jpg"},
    {"src": "image-64f58886-e2e3-497b-bed0-989baebd9878.png", "dst": "timey-3-camera.jpg"},
    {"src": "image-c549c53c-ac66-42df-b9ef-10cbe748cada.png", "dst": "timey-4-profile.jpg"},
    {"src": "image-3ccf977a-0d08-450b-88f2-eeba67101ca3.png", "dst": "timey-5-trending.jpg"},
    {"src": "image-5e1419c6-713b-4479-a029-f7c0f9f4e6f7.png", "dst": "timey-6-tips.jpg"},
    {"src": "image-8db28790-6b6f-4286-8372-7af7741ca044.png", "dst": "timey-7-call.jpg", "letterbox": True},
    {"src": "image-5479179a-6d6d-4089-ba11-ee717008fa4d.png", "dst": "timey-8-splash.jpg", "crop_bottom": True},
]


def main():
    os.makedirs(DST_DIR, exist_ok=True)
    for job in JOBS:
        im = Image.open(os.path.join(SRC_DIR, job["src"]))
        out = mockup(
            im,
            letterbox=job.get("letterbox", False),
            crop_bottom=job.get("crop_bottom", False),
        )
        dest = os.path.join(DST_DIR, job["dst"])
        out.save(dest, "JPEG", quality=86, optimize=True, progressive=True)
        print(f"{job['dst']}: {out.size}  {os.path.getsize(dest)} bytes")


if __name__ == "__main__":
    main()
