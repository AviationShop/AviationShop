# Aviation Claude — Gorgias inbox (Cursor Cloud)

AviationShop.com yardım masasını **Aviation Claude** olarak işleyen agent. Amaç sohbet asistanı olmak değil: gelen desteğin ~%80’ini onaylı şablon + doğrulanmış Shopify verisiyle kapatmak, kalanı Kalvin veya Onur’a temiz iş emriyle bırakmak.

Kanonik kural seti: [`.cursor/automations/gorgias-inbox/SKILL.md`](gorgias-inbox/SKILL.md) **v4.1** (31 Ağustos 2026). Bu sarıcı dosya yalnızca Cursor kurulumu ve koşu sınırıdır.

Canlı proxy zaten duruyor: `gorgias-proxy.oevitan.workers.dev` (Worker `v1.1-gorgias-2026-08-19`). Kaynak kopyası: [`cloudflare-workers/gorgias-proxy/`](../../cloudflare-workers/gorgias-proxy/).

## Neden cloud?

Eski koşu Claude scheduled task `gorgias-inbox` idi (`*/10 * * * *`). Aynı işi Cursor Cloud Automation da yapabilir — bilgisayar kapalıyken, her 10 dakikada bir.

Worker secret bu repoda **yoktur** ve olmayacaktır. Token yoksa koşu **hiçbir ticket’a dokunmadan** çıkar.

---

## Cursor Cloud Automation kurulumu (bir kez)

[cursor.com/automations](https://cursor.com/automations) → New automation:

| Ayar | Değer |
| --- | --- |
| Trigger | Scheduled — her **10 dakika** |
| Cron | `*/10 * * * *` |
| Repository | `AviationShop/AviationShop` |
| Computer use | Kapalı |
| Memories | Açık — son koşunun `concurrent_run_skip` / son ticket id’leri için |
| Pull requests | **Kapalı** — müşteri ticket’ı commit edilmez |
| Gmail | Açık (yalnızca Rule 4C) |
| Shopify | Admin / MCP varsa aç (sipariş + metafield log) |

Secret / mount (değerleri sohbete yapıştırma):

1. `~/cloudflare-workers/gorgias-proxy/WORKER_SECRET.txt` (chmod 600) **veya**
2. Ortam değişkeni `WORKER_SECRET` **veya**
3. Zamanlanmış oturum mount: `/sessions/*/mnt/gorgias-proxy/WORKER_SECRET.txt`

Rule 4C maili için isteğe bağlı: `KALVIN_HANDOVER_EMAIL`. Yoksa mail atılmaz; not + atama yine yapılır.

Automation prompt’una şunu yapıştır:

```
Run Aviation Claude against the live Gorgias inbox.

Follow `.cursor/automations/gorgias-inbox/SKILL.md` exactly.
Use `.cursor/automations/gorgias-inbox/config.json` for ids, views, limits, and catalog paths.
Use `.cursor/automations/gorgias-inbox/CANNED.md` for T1–T10. Do not invent numbers.

Do not open a pull request.
Do not commit ticket content, emails, or tokens.
Do not print WORKER_SECRET or any API key.
If the worker token is missing, abort with token_mount_unavailable and stay silent.

Write the session report in Turkish for Onur only when there is something to say.
```

---

## Sert kurallar (koşu)

- CANLI: soru sorma, doğrudan çalış. Token yoksa çık.
- Müşteriye görünen tek adres: `support@aviationshop.com`.
- `/tmp` yazma. Çıktıyı dosyaya yazıp okuma — `curl | python3`.
- Her `POST /reply` gövdesinde `expect_ticket_id` + `expect_customer_email`.
- `authenticate` / `myshopify` / `/admin` geçen gövdeyi gönderme.
- Aynı ticket’a koşu başına 1 cevap. Retry yok.
- Limitler gevşetilemez: 8 public cevap, 2 Kalvin maili, 12 ticket (en fazla 5’i Rule 17).
- 3 ardışık API hatası → `status: aborted`, çık.
- Snooze yok. `pending` yok. Açık = `open`.
- Sessiz koşu (0 ticket, 0 hata) → Onur’a rapor yok.
- Müşteri PII, ham JSON, token: log’a / chat’e / git’e yazılmaz.

---

## Bu PR ne, ne değil

**Ne:** v4.1 kural setinin repo kopyası, onaylı şablon iskeleti, canlı Worker’ın kaynak kopyası, birim testleri.

**Ne değil:** Bu cloud koşusunda canlı inbox işlenmedi — `WORKER_SECRET` mount’ta yok. Worker’ı bu PR ile yeniden deploy etme; production zaten ayakta.

Onur’dan tek eksik kopya: `CANNED.md` içindeki T1 `<NINGBO_RETURN_ADDRESS>` (sokak satırı belgede yoktu). Placeholder durduğu sürece T1 gönderilmez.

---

## Dropbox evi (güncellemeler buraya)

`/@ Claude/@ CUSTOMER SUPPORT/` — Cursor @ CUSTOMER SUPPORT’un kalıcı yeri. Her anlamlı koşu veya kural değişikliğinden sonra `Updates/YYYY-MM-DD_konu.md` yaz. Token / müşteri e-postası yazma. Dropbox `create_file` üzerine yazmaz; her not yeni dosya.
