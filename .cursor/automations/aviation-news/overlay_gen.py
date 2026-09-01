#!/usr/bin/env python3
"""Deterministic overlay for Aviation News social posts.

Story: 1080x1920 from raw 9:16. Feed: 1080x1080 from raw 1:1.
Exit: 0 OK, 2 input/font, 3 letterbox (no file written).
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W_STORY, H_STORY = 1080, 1920
W_FEED, H_FEED = 1080, 1080
BRAND_BLUE = (21, 70, 198)
BREAKING_RED = (255, 34, 34)
FEED_FOOTER_FG = (216, 224, 245)


def die(code: int, msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_image(raw: str) -> Image.Image:
    if raw.startswith("http://") or raw.startswith("https://"):
        req = urllib.request.Request(
            raw,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        im = Image.open(io.BytesIO(data))
    else:
        im = Image.open(raw)
    return im.convert("RGB")


def cover_fit(im: Image.Image, tw: int, th: int) -> Image.Image:
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def find_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    names = (
        [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for p in names:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    die(2, "FONT_MISSING")
    raise AssertionError


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def region_edge_score(im: Image.Image) -> str:
    small = im.resize((108, 192), Image.Resampling.BILINEAR).convert("L")
    edges = small.filter(ImageFilter.FIND_EDGES)
    h = edges.size[1]
    bands = []
    for i in range(3):
        y0, y1 = i * h // 3, (i + 1) * h // 3
        crop = edges.crop((0, y0, edges.size[0], y1))
        acc = 0
        n = 0
        for px in crop.getdata():
            acc += px
            n += 1
        bands.append(acc / max(n, 1))
    idx = bands.index(min(bands))
    return ("top", "middle", "bottom")[idx]


def letterbox_fail(im: Image.Image) -> bool:
    w, h = im.size
    band = max(1, int(h * 0.12))
    for box in ((0, 0, w, band), (0, h - band, w, h)):
        crop = im.crop(box).convert("L")
        pixels = list(crop.getdata())
        if not pixels:
            return True
        avg = sum(pixels) / len(pixels)
        if avg < 8 or avg > 247:
            return True
    return False


def badge_label(badge: str) -> str:
    b = (badge or "AVIATION NEWS").replace("_", " ").strip().upper()
    return b


def draw_story(im: Image.Image, title: str, badge: str, sources: str) -> Image.Image:
    canvas = cover_fit(im, W_STORY, H_STORY)
    band = region_edge_score(canvas)
    overlay = canvas.convert("RGBA")
    scrim = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    draw_s = ImageDraw.Draw(scrim)
    if band == "top":
        draw_s.rectangle((0, 0, W_STORY, 720), fill=(0, 0, 0, 140))
        y = 80
    elif band == "bottom":
        draw_s.rectangle((0, H_STORY - 780, W_STORY, H_STORY), fill=(0, 0, 0, 140))
        y = H_STORY - 700
    else:
        draw_s.rectangle((0, 620, W_STORY, 1300), fill=(0, 0, 0, 140))
        y = 680
    overlay = Image.alpha_composite(overlay, scrim)
    draw = ImageDraw.Draw(overlay)
    font_badge = find_font(True, 28)
    font_title = find_font(True, 50)
    font_src = find_font(False, 28)
    font_brand = find_font(True, 26)
    label = badge_label(badge)
    fill = BREAKING_RED if "BREAKING" in label else (0, 0, 0, 153)
    tb = draw.textbbox((0, 0), label, font=font_badge)
    pw, ph = tb[2] - tb[0] + 36, tb[3] - tb[1] + 20
    draw.rounded_rectangle((48, y, 48 + pw, y + ph), radius=18, fill=fill)
    draw.text((66, y + 8), label, font=font_badge, fill=(0, 120, 215) if "BREAKING" not in label else (255, 255, 255))
    y += ph + 28
    lines = wrap_text(draw, title, font_title, 980)
    for line in lines:
        draw.text((48, y), line, font=font_title, fill=(255, 255, 255))
        y += 62
    draw.rectangle((48, y + 8, 280, y + 16), fill=BRAND_BLUE)
    y += 36
    src_line = f"✓ Sources: {sources}" if sources else "✓ Sources"
    draw.text((48, y), src_line, font=font_src, fill=(230, 230, 230))
    draw.text((W_STORY - 48, H_STORY - 64), "aviationshop.com", font=font_brand, fill=(255, 255, 255), anchor="rd")
    return overlay.convert("RGB")


def draw_feed(im: Image.Image, title: str, badge: str) -> Image.Image:
    canvas = cover_fit(im, W_FEED, H_FEED).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, W_FEED, 6), fill=BRAND_BLUE)
    font_badge = find_font(True, 24)
    label = "⚡ " + badge_label(badge)
    tb = draw.textbbox((0, 0), label, font=font_badge)
    pw, ph = tb[2] - tb[0] + 28, tb[3] - tb[1] + 16
    draw.rounded_rectangle((24, 24, 24 + pw, 24 + ph), radius=14, fill=(0, 0, 0, 160))
    draw.text((38, 30), label, font=font_badge, fill=(255, 255, 255))
    size = 46
    lines: list[str] = []
    font_title = find_font(True, size)
    while size >= 32:
        font_title = find_font(True, size)
        lines = wrap_text(draw, title, font_title, 1000)
        if len(lines) <= 5:
            break
        size -= 2
    lines = lines[:5]
    y = 90
    for line in lines:
        draw.text((40, y), line, font=font_title, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y += size + 8
    draw.rectangle((0, H_FEED - 72, W_FEED, H_FEED), fill=BRAND_BLUE)
    font_f = find_font(True, 28)
    draw.text((32, H_FEED - 52), "@aviatorszone", font=font_f, fill=(255, 255, 255))
    draw.text((W_FEED - 32, H_FEED - 52), "aviationshop.com", font=font_f, fill=FEED_FOOTER_FG, anchor="rd")
    return canvas.convert("RGB")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True)
    p.add_argument("--aspect", required=True, choices=("story", "feed"))
    p.add_argument("--title", required=True)
    p.add_argument("--badge", default="AVIATION NEWS")
    p.add_argument("--sources", default="")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    try:
        src = load_image(args.raw)
    except Exception as e:
        die(2, f"INPUT {e}")
    if args.aspect == "story":
        out = draw_story(src, args.title, args.badge, args.sources)
    else:
        out = draw_feed(src, args.title, args.badge)
    if letterbox_fail(out):
        die(3, "LETTERBOX")
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
