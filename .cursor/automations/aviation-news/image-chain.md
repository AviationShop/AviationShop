# Image chain — Grok first (permanent)

Eski kural (Gemini-first, 2026-08-31 doküman) **geçersiz**. Bu dosya ezer.

## Sıra

| Katman | Ne | Ne zaman |
| --- | --- | --- |
| 1 | Higgsfield `grok_image_2_0` | varsayılan, 3 aspect paralel |
| 2 | Higgsfield `gpt_image_2` veya `nano_banana_pro` | Grok fail / 401 değilse model hatası |
| 3 | `POST .../generate-async` Gemini `gemini-3-pro-image-preview` persist:true | Higgsfield MCP ölü **ve** `WORKER_AUTH_TOKEN` var |

Higgsfield 401 → `higgsfield_unavailable: yes` LOUD. Gemini last resort. İkisi de yoksa hikâye düşer (`stopped_at: step3_image_generate`). Sessiz düşürme yok.

OpenAI worker `/generate-openai-async` **kullanılmaz** (sonsuz PENDING).

## Aspect

Her hikâye: `16:9` (hero) · `1:1` (feed) · `9:16` (story). 16:9’dan kırpma yasak.

9:16 prompt’a: aircraft HORIZONTALLY across the MIDDLE, wings level, full wingspan, NOT tilted/diagonal/steep-climb.

## Livery / scene

`story_class`: kaza veya taşıyıcının kendi haberi → `livery_critical` (¾, kuyruk okunur). Rota/filo duyurusu → `livery_neutral`.

FIX-LIVERY 4 madde: kuyruk renk+amblem; gövde titles tam metin bir kez; tescil formatı üretilmez; wordmark EXACTLY ONCE.

FIX-ENGINE: intake tek düz halka, tek spinner, tek sıra eşit fan, pilon bağlı.

Prompt’ta `fire/smoke/crash/wreckage/emergency/evacuation` yok.

Sahne: `scene_idx = sum(key bytes) % 12`. Shot: `(sum // 12) % 11`. Aynı koşumda aynı (scene,shot) yok.

## Persist

Higgsfield CDN kalıcı değildir. İndir → JPEG q92 → `POST /persist-bytes` Content-Type `image/jpeg` `--data-binary`. 401 ise `persist_kv.py` (CLOUDFLARE_API_TOKEN → KV IMAGES). Yanıt/doğrulanmış URL birebir. GET 200 + `image/jpeg`.

Shopify Files kaynak gerçek değildir.

## QC (blocking, gözle)

1 dikey kuyruk · doğru motor sayısı · dorsal kanat yok · kopya parça yok · wordmark okunur · iniş takımı erimemiş · tip imzası (A350 raccoon-mask + Trent XWB). 9:16 rotasyon fail → hikâye düşer.

Worker `POST /qc` advisory.
