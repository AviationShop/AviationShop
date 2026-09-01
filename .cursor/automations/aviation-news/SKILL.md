# Aviation News launcher (Cloud)

Her slotta bu dosyayı **önce** oku. Alt dosyalar launcher’ı ezmez — çelişirse burası geçerli.

## Bu koşunun işi

1. Secret smoke — **Grok Mini yolu:** Dropbox Mini skill oku, curl header’ı kullan (`secrets.md`). Cursor env’e sosyal secret koyma.
2. Publisher pass — hedef `TARGET_PUBLISHED=3` (owner 4 demedikçe)
3. Distributor: overlay Python + persist worker + sosyal **worker POST** (direkt Storrito/Graph yok)
4. Türkçe owner raporu (Onur Evitan)

PR açma. Tema değiştirme. Shopify Files’a görsel yükleme.

## Hard rules

- **KURAL SIFIR:** `articleCreate` / `articleUpdate` gövdesine `image` koyma. `fileCreate` yok. Hero = metafield `aviation_news.hero_image_url` = persist URL.
- **Görsel yoksa yayın yok.**
- Freshness ≤96h, tarih yoksa RED. Aggregator kaynak sayılmaz.
- ≥2 bağımsız Tier-1 **yalnız ölümlü/ciddi kaza** için zorunlu. Minör/ticari (rota, tarife, filo, sipariş) tek güvenilir havacılık kaynağıyla geçer.
- Yasak konular: LATAM merkezli, yeni/özel livery tanıtımı, op-ed, evergreen listicle, terminal/lounge/ground handling.
- Askerî: koşumda max 1, günde max 2. Savaş/ölü-yaralı yok.
- urllib/requests → CF 1010. `curl` + browser UA.
- Mac Mini publisher ile paralel çalışma yok.
- **IG Story:** yalnız `storrito-story-poster` `POST /schedule` + `x-poster-secret` = Mini skill **All Worker Auth** (Bearer kelimesi yok). `storrito.com` yok. Mini Part 2 Storrito Bearer kopyalanmaz.
- **Kapı = Grok Mini skill.** Dropbox `distributor-SKILL.md` Step 1. Cursor env’e `POSTER_SECRET` / `WORKER_AUTH_TOKEN` koyma, owner’a yapıştır deme. Drive’da secret dosyası yok (boş tarama doğru). Dropbox skill **okumak** Grok yoludur, secret-dosyası avı değil.

## Image chain (kalıcı — Gemini-first’ü ezer)

1. Cursor **GenerateImage** (Grok Image 2) — 16:9, 1:1, 9:16
2. Higgsfield MCP yedek — `grok_image_2_0` (bağlıysa). Kurulum: `higgsfield.md`
3. Higgsfield `gpt_image_2` / `nano_banana_pro`
4. Gemini worker `/generate-async` — last resort

Ayrıntı: `image-chain.md`.

## Exit dictionary (`stopped_at`)

`IN_PROGRESS` · `step0_skill_read` · `step1_feed_fetch` · `step2_freshness` · `step2_dedup` · `step3_image_generate` · `step4_persist_bytes` · `step4_image_qc` · `step5_factgate` · `step5_article_create` · `step5_hero_metafield` · `step6_ledger_insert` · `completed_full` · `completed_partial` · `healthy_early_exit` · `real_lull` · `auth_blocked` · `higgsfield_unauthorized` · `unhandled_error`

Runlog: shop metafield `aviation_news.publisher_runlog` (son 20). FAZ A Step 0’da `IN_PROGRESS`. FAZ B her çıkışta aynı `run_id` güncelle.

## LOUD-FAIL

Havuz <12 ve taze allow item varken 0 yayın → raporun ilk satırı `🔴 SILENT-FAIL DETECTED`.

## Workers

Post + persist worker’da. Shopify ve Higgsfield burada yok. Tam tablo: `architecture.md`.

| Worker | URL |
| --- | --- |
| ledger | `https://aviation-news-ledger.oevitan.workers.dev` |
| persist | `https://gemini-image-worker.oevitan.workers.dev` |
| IG Story | `https://storrito-story-poster.oevitan.workers.dev` |
| IG Feed | `https://soft-snow-c1c2.oevitan.workers.dev` |
| Facebook | `https://facebook-page-poster.oevitan.workers.dev` |
| feed-proxy | `https://news-feed-proxy.oevitan.workers.dev` |

D1 `aviation-blog` `32af39ea-7291-40cc-9768-bd63675befee` — MCP query dedup’a yardımcı olur; insert tercihen `POST /ledger-add`.
