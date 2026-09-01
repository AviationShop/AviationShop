# Aviation News — Cursor Cloud pipeline

Mac Mini Claude Cowork cron’unun yerine geçen **tek pipeline**. Publisher + distributor aynı otomasyonda, günde **6 slot**.

Canlı servisler Cloudflare Workers’ta kalır. Bu klasör yalnızca orkestrasyon skill’idir.

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
2. `secrets.md` — env / MCP kapıları (eksikse yayın yok)
3. `publisher.md` — aday → yaz → görsel → Shopify → D1
4. `image-chain.md` — Grok-first kalıcı kural
5. `distributor.md` — overlay + sosyal (secret yoksa dur)
6. `watchdog.md` — 5 saatlik dead-man (ayrı otomasyon)

## Cutover

Mac Mini `aviation-news-publisher` / `distributor` / `gap-watchdog` cron’ları **aynı anda çalışmamalı**. Çift yayın riski.

## Cursor Automation

`schedule.md` içindeki prompt’u [cursor.com/automations](https://cursor.com/automations) yeni kayda yapıştır.
