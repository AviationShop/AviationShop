# Cursor Automation — draft

[cursor.com/automations](https://cursor.com/automations) → New automation.

## Publisher+distributor (6×/gün)

| Ayar | Değer |
| --- | --- |
| Name | Aviation News pipeline |
| Trigger | Scheduled, timezone `Europe/Istanbul` |
| Cron | `0 0,4,8,12,16,20 * * *` |
| Repository | `AviationShop/AviationShop` |
| Pull requests | Kapalı |
| Computer use | Kapalı (görsel Cursor GenerateImage + curl) |
| Environment secrets | `SHOPIFY_*` + **`WORKER_AUTH_TOKEN`** + `POSTER_SECRET` |
| MCP (ayrı, OAuth) | Higgsfield yedek — `higgsfield.md`; Grok Image 2 için zorunlu değil |

Prompt:

```
Run the Aviation News publisher+distributor pipeline for this slot.

Follow `.cursor/automations/aviation-news/SKILL.md` exactly.
Then publisher.md, image-chain.md, secrets.md. After publish, distributor.md.

TARGET_PUBLISHED = 3 unless the owner already confirmed 4.
Grok Image 2 via Cursor GenerateImage first; Higgsfield grok_image_2_0 backup if MCP is logged in; Gemini /generate-async last resort.
Do not set article.image. Persist images via worker /persist-bytes. No Shopify Files.
Do not run if Mac Mini publisher cron is still enabled (double-publish).
Do not open a pull request.
Write the slot report in Turkish for Onur Evitan.
Store: $SHOPIFY_FLAG_STORE / aviationshop.com News blog.
```

## Watchdog (saatlik)

| Ayar | Değer |
| --- | --- |
| Cron | `8 * * * *` Europe/Istanbul (eski :08) |
| Prompt | Follow `.cursor/automations/aviation-news/watchdog.md`. Threshold 5.0h. Turkish report. No PR. |

## Enable etmeden önce

1. Env’de `WORKER_AUTH_TOKEN` + `POSTER_SECRET` var (sosyal POST için)
2. Higgsfield isteğe bağlı yedek — Cloud MCP menüsünden login (`higgsfield.md`)
3. Mac Mini publisher/distributor/watchdog cron **kapalı**
4. Bir slot manuel (bu skill ile) yeşil
