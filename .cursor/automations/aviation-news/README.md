# Aviation News — Cursor Cloud pipeline

Mac Mini Claude Cowork cron’unun yerine geçen **tek pipeline**. Publisher + distributor aynı otomasyonda, günde **6 slot**.

Canlı **post + persist** Cloudflare Workers’ta. Bu klasör **orkestrasyon**: overlay Python, Shopify Admin, Higgsfield/Grok görsel. Ayrıntı: `architecture.md`.

## Slot (Europe/Istanbul)

| TR | UTC (TR+3) |
| --- | --- |
| 00:00 | 21:00 |
| 04:00 | 01:00 |
| 08:00 | 05:00 |
| 12:00 | 09:00 |
| 16:00 | 13:00 |
| 20:00 | 17:00 |

Cron (UTC): `0 21,1,5,9,13,17 * * *`  
Cron (Istanbul): `0 0,4,8,12,16,20 * * *`

**TARGET_PUBLISHED = 3** (~18/gün). Owner 4 isterse `~24/gün`. Eski Mac Mini: 4×5 ≈ 20/gün.

## Bu koşuda oku (sırayla)

1. `SKILL.md` — launcher, hard rules, exit paths
2. `architecture.md` — orkestrasyon vs worker (post worker atar)
3. `secrets.md` — wrangler secret **adları** + HTTP kapısı. Drive’da secret yok.
4. `publisher.md` — aday → yaz → görsel → Shopify → D1
5. `image-chain.md` — Grok Image 2 (Cursor) first; Higgsfield yedek
6. `higgsfield.md` — Cloud MCP OAuth (env secret değil)
7. `distributor.md` — overlay Python + worker POST (direkt Storrito yok)
8. `watchdog.md` — 5 saatlik dead-man (ayrı otomasyon)

## Cutover

Mac Mini `aviation-news-publisher` / `distributor` / `gap-watchdog` cron’ları **aynı anda çalışmamalı**. Çift yayın riski.

## Cursor Automation

`schedule.md` içindeki prompt’u [cursor.com/automations](https://cursor.com/automations) yeni kayda yapıştır.
