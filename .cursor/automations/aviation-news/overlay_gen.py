# 2026-07-24: footer bandi AviationShop mavisi #1546C6 + Sources clipping fix — Onur onayi
# Son güncelleme: 2026-06-22 — kanonik deterministik overlay üreteci (per-run re-port YASAK)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
overlay_gen.py — AviationShop / @piloteyes737 KANONIK deterministik overlay üreteci.

Bu dosya `overlay-functions.js` (createStoryOverlay / createFeedOverlay v3.0) dosyasinin
SADIK Pillow port'udur. Distributor her kosuda overlay'i SIFIRDAN port etmek YERINE
SADECE bu script'i cagirir (per-run re-port YASAK — kirilgan/tutarsiz davranisin koku oydu).

KULLANIM:
  python3 overlay_gen.py --raw <CDN_URL> --aspect <story|feed> \
      --title "<TAM BASLIK>" --badge "AVIATION NEWS" \
      --sources "<sources_short>" --out <path.png>

  story -> 1080x1920, KAYNAK = raw_9_16   (zaten 9:16)
  feed  -> 1080x1080, KAYNAK = raw_1_1    (zaten 1:1)

KAYNAK = COVER-fit (fill + center-crop). letterbox/contain/siyah-padding YOK,
stretch-distort YOK. Dogru kaynak (9:16 -> story, 1:1 -> feed) zaten canvas
aspect'iyle eslestiginden cover = temiz dolum.

ZORUNLU SELF-CHECK: cikti uretildikten sonra ust+alt %12 bandi olculur; neredeyse
tek-renk siyah ise (letterbox) -> exit code 3, stderr'e "LETTERBOX" yazilir, dosya
YAZILMAZ. (Dogru kaynak verilince tetiklenmez; yanlis 16:9 kaynak icin guvenlik agi.)

Cikis kodlari: 0 OK | 2 girdi/yukleme hatasi | 3 LETTERBOX (dosya yazilmadi)
"""

import argparse
import io
import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Fonts — JS bold Arial/Helvetica kullaniyor; Linux'ta metric-uyumlu Liberation Sans.
# ---------------------------------------------------------------------------
_FONT_DIRS = [
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/liberation2",
    os.path.dirname(os.path.abspath(__file__)),
]
_BOLD_NAMES = ["LiberationSans-Bold.ttf", "Arial-Bold.ttf", "arialbd.ttf"]
_REG_NAMES = ["LiberationSans-Regular.ttf", "Arial.ttf", "arial.ttf"]


def _find_font(names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


_BOLD_PATH = _find_font(_BOLD_NAMES)
_REG_PATH = _find_font(_REG_NAMES)
if not _BOLD_PATH or not _REG_PATH:
    sys.stderr.write(
        "FONT_MISSING: Liberation Sans bulunamadi. "
        "Kur: apt-get install -y fonts-liberation\n"
    )
    sys.exit(2)

_FONT_CACHE = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(_BOLD_PATH if bold else _REG_PATH, size)
    return _FONT_CACHE[key]


# ---------------------------------------------------------------------------
# Yardimcilar — JS wrapText() / drawRoundedRect() / measureText() esdegerleri
# ---------------------------------------------------------------------------
def _text_w(draw, text, fnt):
    """Canvas ctx.measureText(text).width esdegeri."""
    return draw.textlength(text, font=fnt)


def wrap_text(draw, text, fnt, max_width):
    """overlay-functions.js wrapText() ile birebir kelime sarmasi."""
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w) if cur else w
        if _text_w(draw, test, fnt) > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def cover_fit(img, W, H):
    """
    COVER (fill + center-crop): kaynagi en-boy oranini KORUYARAK canvas'i tamamen
    dolduracak sekilde olcekler, tasan kismi merkezden kirpar.
    Letterbox/contain/siyah-padding URETMEZ; stretch-distort URETMEZ.
    """
    img = img.convert("RGB")
    sw, sh = img.size
    scale = max(W / sw, H / sh)
    nw, nh = max(W, int(round(sw * scale))), max(H, int(round(sh * scale)))
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    return img.crop((left, top, left + W, top + H))


def _interp_stops(t, stops):
    """t in [0,1] icin renk-stop listesinden ALPHA interpolasyonu (canvas clamp semantigi)."""
    if t <= stops[0][0]:
        return stops[0][1]
    if t >= stops[-1][0]:
        return stops[-1][1]
    for i in range(1, len(stops)):
        p0, a0 = stops[i - 1]
        p1, a1 = stops[i]
        if t <= p1:
            f = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
            return a0 + (a1 - a0) * f
    return stops[-1][1]


def linear_scrim(base, y0, y1, stops, fill_y, fill_h):
    """
    JS createLinearGradient(0,y0,0,y1) + fillRect(0,fill_y,W,fill_h) esdegeri.
    Renk siyah; stops = [(pos0,alpha0),...]. fill bolgesindeki her satir icin
    t=clamp((y-y0)/(y1-y0)) -> alpha -> siyahi base uzerine alpha-composite eder.
    """
    W = base.width
    fy0 = max(0, int(round(fill_y)))
    fy1 = min(base.height, int(round(fill_y + fill_h)))
    if fy1 <= fy0:
        return
    span = (y1 - y0) if (y1 - y0) != 0 else 1.0
    px = base.load()
    for y in range(fy0, fy1):
        t = (y - y0) / span
        if t < 0:
            t = 0.0
        elif t > 1:
            t = 1.0
        a = _interp_stops(t, stops)
        if a <= 0:
            continue
        ia = 1.0 - a
        for x in range(W):
            r, g, b = px[x, y]
            px[x, y] = (int(r * ia), int(g * ia), int(b * ia))


def rounded_rect(draw, x, y, w, h, r, fill):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)


def draw_text_shadow(draw, xy, text, fnt, fill, shadow=(0, 0, 0, 200), off=(2, 2)):
    """JS shadowColor/offset esdegeri — once offsetli koyu golge, sonra ana metin."""
    x, y = xy
    sr, sg, sb, sa = shadow
    draw.text((x + off[0], y + off[1]), text, font=fnt, fill=(sr, sg, sb, sa))
    draw.text((x, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------------------
# Edge-score (regionEdgeScore) — JS ile birebir: 108xH' downsample, Sobel benzeri
# parlaklik gradyani; en sakin (en dusuk skor) banda headline.
# ---------------------------------------------------------------------------
def region_edge_score(pix, aW, aH, y_start, y_end):
    total = 0.0
    count = 0
    ys = max(1, y_start)
    ye = min(aH - 1, y_end)
    for y in range(ys, ye):
        for x in range(1, aW - 1):
            l = pix[x - 1, y]
            r = pix[x + 1, y]
            u = pix[x, y - 1]
            d = pix[x, y + 1]
            lum_r = r[0] * 0.299 + r[1] * 0.587 + r[2] * 0.114
            lum_l = l[0] * 0.299 + l[1] * 0.587 + l[2] * 0.114
            lum_d = d[0] * 0.299 + d[1] * 0.587 + d[2] * 0.114
            lum_u = u[0] * 0.299 + u[1] * 0.587 + u[2] * 0.114
            gx = abs(lum_r - lum_l)
            gy = abs(lum_d - lum_u)
            total += math.sqrt(gx * gx + gy * gy)
            count += 1
    return (total / count) if count > 0 else 0.0


def pick_placement(src):
    """JS createStoryOverlay edge-score yerlesim secimi (top/middle/bottom)."""
    aW, aH = 108, 192
    small = src.resize((aW, aH), Image.BILINEAR).convert("RGB")
    pix = small.load()
    third = aH // 3
    top = region_edge_score(pix, aW, aH, 0, third)
    mid = region_edge_score(pix, aW, aH, third, third * 2)
    bot = region_edge_score(pix, aW, aH, third * 2, aH)
    if bot <= top and bot <= mid:
        placement = "bottom"
    elif top <= bot and top <= mid:
        placement = "top"
    else:
        placement = "middle"
    return placement, (top, mid, bot)


# ---------------------------------------------------------------------------
# Badge config (JS badgeConfig) — feed etiketleri ⚡ onekli; renkler birebir.
# ---------------------------------------------------------------------------
BADGE_CONFIG = {
    "BREAKING": {"color": (0xFF, 0x22, 0x22), "label": "BREAKING"},
    "AVIATION NEWS": {"color": (0x00, 0x78, 0xFF), "label": "AVIATION NEWS"},
    "JUST IN": {"color": (0xFF, 0x8C, 0x00), "label": "JUST IN"},
    "DEVELOPING": {"color": (0xFF, 0xD7, 0x00), "label": "DEVELOPING"},
}
BOLT = "⚡"  # ⚡ — Liberation'da glyph yoksa otomatik dusurulur (asagida kontrol)

# AviationShop MARKA MAVISI — canli V36 tema top/bottom
# info-bar customFillColor + header accentColor degeri: #1546C6 (rgb 21,70,198).
# Feed (1:1) alt footer seridi bu renkte basilir.
BRAND_BLUE = (0x15, 0x46, 0xC6)  # #1546C6


def _bolt_prefix(fnt):
    """Liberation Sans ⚡ glyph'ini renderlayamiyorsa oneki dusur (tofu uretme)."""
    try:
        from PIL import Image as _I
        d = ImageDraw.Draw(_I.new("RGB", (10, 10)))
        return (BOLT + " ") if d.textlength(BOLT, font=fnt) > 0 else ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# STORY OVERLAY (9:16, 1080x1920) — createStoryOverlay portu
# ---------------------------------------------------------------------------
def build_story(src, headline, badge_type, sources_line):
    W, H = 1080, 1920
    placement, scores = pick_placement(src)

    base = cover_fit(src, W, H)
    # gradient scrim'ler placement'a gore (JS stops birebir)
    if placement == "bottom":
        linear_scrim(base, 0, H * 0.20, [(0, 0.60), (1, 0.0)], 0, H * 0.20)
        linear_scrim(base, H * 0.35, H, [(0, 0.0), (1, 0.90)], H * 0.35, H * 0.65)
    elif placement == "top":
        linear_scrim(base, 0, H * 0.55, [(0, 0.90), (1, 0.0)], 0, H * 0.55)
        linear_scrim(base, H * 0.85, H, [(0, 0.0), (1, 0.40)], H * 0.85, H * 0.15)
    else:
        linear_scrim(base, H * 0.20, H * 0.75,
                     [(0, 0.0), (0.3, 0.75), (0.7, 0.75), (1, 0.0)], H * 0.20, H * 0.55)
        linear_scrim(base, H * 0.85, H, [(0, 0.0), (1, 0.40)], H * 0.85, H * 0.15)

    base = base.convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")

    bt = (badge_type or "AVIATION NEWS").upper()
    pill_text = "BREAKING" if bt == "BREAKING" else "AVIATION NEWS"
    pill_font = font(28, bold=True)
    pill_y = 560 if placement == "middle" else 140
    pill_tw = _text_w(draw, pill_text, pill_font)
    pad_x, pad_y = 14, 8
    pill_x = 48
    pill_w = pill_tw + pad_x * 2
    pill_h = 28 + pad_y * 2
    if bt == "BREAKING":
        rounded_rect(draw, pill_x, pill_y, pill_w, pill_h, 8, (0xFF, 0x22, 0x22, 255))
        pill_fill = (255, 255, 255, 255)
    else:
        rounded_rect(draw, pill_x, pill_y, pill_w, pill_h, 8, (0, 0, 0, 153))  # rgba(0,0,0,0.60)
        pill_fill = (0, 120, 215, 255)
    draw.text((pill_x + pad_x, pill_y + pad_y), pill_text, font=pill_font, fill=pill_fill)

    # Headline — TAM title, kisaltma yok; wrap, gerekirse satir.
    hl_text = headline.upper()
    hl_font = font(50, bold=True)
    hl_lines = wrap_text(draw, hl_text, hl_font, 980)
    hl_line_h = 62
    total_block_h = len(hl_lines) * hl_line_h + 112
    if placement == "bottom":
        y_pos = min(1300, 1620 - total_block_h)
        y_pos = max(y_pos, 1050)
    elif placement == "top":
        y_pos = pill_y + pill_h + 40
    else:
        y_pos = (H - total_block_h) / 2 + 80

    for line in hl_lines:
        draw_text_shadow(draw, (48, y_pos), line, hl_font, (255, 255, 255, 255),
                         shadow=(0, 0, 0, 204), off=(2, 2))
        y_pos += hl_line_h

    bar_y = y_pos + 20
    draw.rectangle([48, bar_y, 48 + 60, bar_y + 4], fill=(0, 120, 215, 255))
    draw.text((48, bar_y + 36), "AviationShop.com | Daily Aviation News",
              font=font(24, bold=False), fill=(255, 255, 255, 178))
    draw.text((48, bar_y + 64), sources_line or "✓ Verified from multiple sources",
              font=font(20, bold=False), fill=(255, 255, 255, 128))

    wm_font = font(22, bold=False)
    wm = "aviationshop.com"
    wm_w = _text_w(draw, wm, wm_font)
    draw.text((W - wm_w - 32, H - 32 - 22), wm, font=wm_font, fill=(255, 255, 255, 102))

    return base.convert("RGB"), {"placement": placement, "scores": scores,
                                 "hl_lines": len(hl_lines)}


# ---------------------------------------------------------------------------
# FEED OVERLAY (1:1, 1080x1080) — createFeedOverlay portu
# ---------------------------------------------------------------------------
def build_feed(src, headline, badge_type, sources_line):
    W, H = 1080, 1080
    base = cover_fit(src, W, H).convert("RGB")

    bt = (badge_type or "AVIATION NEWS").upper()
    cfg = BADGE_CONFIG.get(bt, BADGE_CONFIG["AVIATION NEWS"])
    color = cfg["color"]

    # gradient scrim'ler (JS stops) — once
    linear_scrim(base, 6, H * 0.25, [(0, 0.70), (1, 0.0)], 6, H * 0.25 - 6)
    linear_scrim(base, H * 0.35, H, [(0, 0.0), (1, 0.90)], H * 0.35, H * 0.65)
    base = base.convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")
    # ust renk seridi (6px) — scrim'den sonra ciz ki net kalsin
    draw.rectangle([0, 0, W, 6], fill=(color[0], color[1], color[2], 255))

    pill_font = font(28, bold=True)
    bolt = _bolt_prefix(pill_font)
    pill_text = bolt + cfg["label"]
    pill_tw = _text_w(draw, pill_text, pill_font)
    pad_x, pad_y = 16, 10
    pill_x, pill_y = 36, 30
    pill_w = pill_tw + pad_x * 2
    pill_h = 28 + pad_y * 2
    rounded_rect(draw, pill_x, pill_y, pill_w, pill_h, 10, (color[0], color[1], color[2], 255))
    draw.text((pill_x + pad_x, pill_y + pad_y), pill_text, font=pill_font, fill=(255, 255, 255, 255))

    # Headline — auto-fit 46->32, maxWidth 1000, maxLines 5; TAM title, kelime atma yok.
    hl_text = headline.upper()
    font_size = 46
    max_lines, max_width = 5, 1000
    hl_lines, hl_line_h, hl_font = None, None, None
    while font_size >= 32:
        hl_font = font(font_size, bold=True)
        hl_lines = wrap_text(draw, hl_text, hl_font, max_width)
        hl_line_h = round(font_size * 1.22)
        if len(hl_lines) <= max_lines:
            break
        font_size -= 2
    if len(hl_lines) > max_lines:
        hl_lines = hl_lines[:max_lines]

    bottom_bar_y = H - 70
    # Sources satiri: footer bandinin TAM USTUNDE, tam gorunur, yeterli bosluk.
    # Eski kod source_base_y = bottom_bar_y - 18 idi; 22px font (yukseklik ~28px)
    # 18px bosluga sigmayip alt banda tasarak kesiliyordu. Simdi metnin gercek
    # yuksekligi (ascent+descent) + sabit bosluk kadar YUKARI konumlanir.
    src_font = font(22, bold=False)
    _sasc, _sdesc = src_font.getmetrics()
    src_h = _sasc + _sdesc
    src_gap = 16  # Sources metninin ALTI ile footer bandi USTU arasi bosluk (px)
    source_base_y = bottom_bar_y - src_gap - src_h
    headline_block_h = len(hl_lines) * hl_line_h
    y_pos = source_base_y - 34 - headline_block_h
    y_pos = max(y_pos, 380)

    for line in hl_lines:
        draw_text_shadow(draw, (36, y_pos), line, hl_font, (255, 255, 255, 255),
                         shadow=(0, 0, 0, 128), off=(2, 2))
        y_pos += hl_line_h

    # Sources — footer bandinin ustunde, koyu scrim uzerinde okunur gri.
    draw_text_shadow(draw, (36, source_base_y),
                     sources_line or "Verified from Multiple Sources", src_font,
                     (0xCC, 0xCC, 0xCC, 255), shadow=(0, 0, 0, 160), off=(1, 1))

    # alt footer seridi — AviationShop MARKA MAVISI (#1546C6), tam opak.
    draw.rectangle([0, bottom_bar_y, W, bottom_bar_y + 70],
                   fill=(BRAND_BLUE[0], BRAND_BLUE[1], BRAND_BLUE[2], 255))  # #1546C6
    hf = font(22, bold=False)
    handle = "@aviatorszone"  # 2026-07-03: @piloteyes737 IG askısı süresince IG dağıtımı @aviatorszone'a yönlendirildi (baked overlay branding). Restore olunca @piloteyes737'u geri al.
    asc, desc = hf.getmetrics()
    ty = bottom_bar_y + 35 - (asc + desc) // 2
    draw.text((24, ty), handle, font=hf, fill=(255, 255, 255, 255))
    rf = font(18, bold=False)
    right_text = "AviationShop.com | Daily Aviation News"
    right_w = _text_w(draw, right_text, rf)
    rasc, rdesc = rf.getmetrics()
    rty = bottom_bar_y + 35 - (rasc + rdesc) // 2
    # Mavi band uzerinde #999 gri dusuk kontrasttir; acik mavi-beyaz tona cekildi.
    draw.text((W - right_w - 24, rty), right_text, font=rf, fill=(0xD8, 0xE0, 0xF5, 255))

    return base.convert("RGB"), {"font_size": font_size, "hl_lines": len(hl_lines)}


# ---------------------------------------------------------------------------
# ZORUNLU SELF-CHECK — ust+alt %12 bandi letterbox (tek-renk siyah) mi?
# ---------------------------------------------------------------------------
def letterbox_check(img):
    """
    Ust ve alt %12 bandi neredeyse tek-renk siyahsa LETTERBOX kabul edilir.
    Donus: (is_letterbox, detay_dict)
    """
    W, H = img.size
    band = max(1, int(round(H * 0.12)))
    small = img.convert("RGB")

    def band_stats(y0, y1):
        crop = small.crop((0, y0, W, y1)).resize((64, 16), Image.BILINEAR).convert("RGB")
        raw = crop.tobytes()  # RGBRGB...
        n = len(raw) // 3
        black = 0
        total = 0
        for i in range(0, len(raw), 3):
            r, g, b = raw[i], raw[i + 1], raw[i + 2]
            if r < 12 and g < 12 and b < 12:
                black += 1
            total += r + g + b
        avg = total / (3 * n)
        return black / n, avg

    tb_black, tb_avg = band_stats(0, band)
    bb_black, bb_avg = band_stats(H - band, H)
    # NOT: alt bandda mesru koyu gradient/siyah-bar var (feed alt bar, story alt scrim),
    # bu yuzden esikler gercek letterbox'i yakalayacak kadar kati tutulur.
    top_letterbox = tb_black > 0.97 and tb_avg < 8
    bot_letterbox = bb_black > 0.985 and bb_avg < 6
    detail = {"top_black": round(tb_black, 3), "top_avg": round(tb_avg, 1),
              "bot_black": round(bb_black, 3), "bot_avg": round(bb_avg, 1)}
    return (top_letterbox or bot_letterbox), detail


# ---------------------------------------------------------------------------
def load_image(src):
    """URL veya yerel dosyadan kaynak gorseli yukler."""
    if src.startswith("http://") or src.startswith("https://"):
        req = urllib.request.Request(
            src,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        return Image.open(io.BytesIO(data))
    return Image.open(src)


def main():
    ap = argparse.ArgumentParser(description="Kanonik deterministik overlay ureteci")
    ap.add_argument("--raw", required=True, help="Kaynak CDN URL veya yerel yol (story=raw_9_16, feed=raw_1_1)")
    ap.add_argument("--aspect", required=True, choices=["story", "feed"])
    ap.add_argument("--title", required=True, help="TAM baslik (kisaltilmaz)")
    ap.add_argument("--badge", default="AVIATION NEWS")
    ap.add_argument("--sources", default="", help="sources_short (bos ise geriye-uyumlu fallback)")
    ap.add_argument("--out", required=True, help="cikti .png yolu")
    args = ap.parse_args()

    try:
        src = load_image(args.raw)
    except Exception as e:
        sys.stderr.write("LOAD_ERROR: %s\n" % e)
        sys.exit(2)

    # Dinamik kaynak satiri (JS sourcesLine semantigi)
    ss = (args.sources or "").strip()
    if args.aspect == "story":
        sources_line = ("✓ Sources: " + ss) if ss else "✓ Verified from multiple sources"
        img, meta = build_story(src, args.title, args.badge, sources_line)
    else:
        sources_line = ("Sources: " + ss) if ss else "Verified from Multiple Sources"
        img, meta = build_feed(src, args.title, args.badge, sources_line)

    # Boyut dogrulamasi
    exp = (1080, 1920) if args.aspect == "story" else (1080, 1080)
    if img.size != exp:
        sys.stderr.write("DIMENSION_ERROR: %s != %s\n" % (img.size, exp))
        sys.exit(2)

    # ZORUNLU SELF-CHECK
    is_lb, detail = letterbox_check(img)
    if is_lb:
        sys.stderr.write("LETTERBOX: ust/alt band tek-renk siyah — yanlis kaynak (16:9?). "
                         "Dosya yazilmadi. detail=%s\n" % detail)
        sys.exit(3)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.save(args.out, "PNG")
    sys.stdout.write("OK %s %s meta=%s letterbox=NO check=%s\n"
                     % (args.aspect, img.size, meta, detail))


if __name__ == "__main__":
    main()
