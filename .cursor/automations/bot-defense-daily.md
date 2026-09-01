# Bot Defense — günlük gözetim raporu

aviationshop.com Cloudflare bot savunmasının **gözetim** görevi.

Sweep’i sen koşmazsın. `botdefense-worker` her gün **09:06 İstanbul**’da Cloudflare’de zaten koşuyor ve WAF kurallarını güncelliyor. Senin işin: arşivi okumak, karşılaştırmak, Onur’a yazmak.

## Senin Mac’in değil — Cursor Cloud Automation

Bu görev Mac mini’deki Cowork görevinin yerini alır. Mac’ten `api.cloudflare.com` / `*.workers.dev` kapalıydı; Cursor Cloud Agent buradan Worker’a ulaşabiliyor.

**Kurulum (bir kez):** [cursor.com/automations](https://cursor.com/automations) → New automation:

| Ayar | Değer |
| --- | --- |
| Trigger | Scheduled, her gün **09:25** Europe/Istanbul (`25 6 * * *` UTC) |
| Repository | `AviationShop/AviationShop` |
| Computer use | Kapalı |
| Pull requests | Kapalı |
| Slack / e-posta | Kapalı — rapor bu agent sohbetine yazılır |

Ortam secret’ı (zorunlu):

- `WORKER_SECRET` — Worker HTTP uçlarını koruyan bearer (Mac’te `.worker_secret` veya Cloudflare Worker secret deposu)

Aşağıdaki metni automation prompt’una yapıştır:

```
Bot savunması günlük gözetimi.

Follow `.cursor/automations/bot-defense-daily.md` exactly.
Run `python3 scripts/botdefense/fetch-last.py` to read today's archive.
Do not open a pull request.
Do not change Cloudflare rules.
Do not send email.
Write to Onur in Turkish in this chat only when a report trigger fires (silence principle).
If a report is needed, also save it to Dropbox reports/.
```

---

## Rol

Onur pilot / tasarımcı, yazılımcı değil. “ASN” yerine “bot ağı”, “ruleset PATCH” yerine “kurala eklendi”. Rakam ver, teknik döküm verme. En fazla birkaç cümle.

Sen sweep’i **KOŞMUYORSUN**. Cloudflare kurallarını **ELLE değiştirmiyorsun**. Token/secret istemiyorsun, ekrana basmıyorsun, dosyaya / sohbete / PR’a koymuyorsun.

## Adım 0 — Arşivi oku

```bash
python3 scripts/botdefense/fetch-last.py
```

Script `WORKER_SECRET` ortam değişkenini kullanır; Worker `GET /last` cevabını stdout’a JSON basar.

Alternatif (Shopify MCP bağlıysa):

```
{ shop { metafield(namespace:"botdefense", key:"run_log") { updatedAt value } } }
```

`value` / `last` son ~30 koşumu tutar. Alanlar: `date`, `ts`, `dry_run`, `stats`, `swept`, `auto_block[]`, `auto_challenge[]`, `review[]`, `block_patch{}`, `challenge_patch{}`, `ip_lookup_ok`, `rule_counts{}`, `text`.

**Durma koşulları:**

- metafield / `/last` boş → “Bot savunması koşuyor ama raporunu arşivleyemiyor olabilir” yaz, DUR.
- Bugünün kaydı yok → bildir, son koşum tarihini yaz, DUR.
- Rapor uydurma, tahmin yürütme, Cloudflare’e dokunma.

## Adım 1 — İlk canlı kural eklemesi

Arşivdeki tüm kayıtlara bak. `dry_run: false` ve `*_patch.applied: true` olan **ilk** kayıt bugün mü?

Öyleyse sessizlik kurallarını es geç ve mutlaka yaz:

> Bot savunması canlıya geçtikten sonra ilk kez bir kural ekledi. Devrin ilk gerçek testi bu.

+ hangi ağ(lar), firma, istek sayısı, engel mi doğrulama mı  
+ eklenen numaralar  
+ “Yanlışsa geri alma: Cloudflare panosu → WAF → Custom rules → numarayı elle sil. Worker’ı durdurmak eklenmiş kuralı geri almaz.”

(Bu eşik 19 Ağustos 2026’da geçildi — artık rutin tetikleyici değil.)

## Adım 2 — Günlük değerlendirme (sessizlik ilkesi)

Bugünü dünle karşılaştır. **Sakin günlerde hiçbir şey yazma.** “Bugün yapacak iş yok” deme.

Yalnızca şu durumlarda yaz:

| # | Durum | Ne yazılır |
| --- | --- | --- |
| a | `auto_block` veya `auto_challenge` dolu | Firma, istek sayısı, aksiyon; `*_patch.applied` ile teyit |
| b | `review` dolu | Onur’a sor — karar onun |
| c | `*_patch.ok = false` | Cloudflare reddetti → LOUD uyarı |
| d | Bot hacmi (block+challenge) düne göre %50+ arttı | Uyarı |
| e | `ip_lookup_ok: false` | Sınıflandırma zayıf → uyarı |
| f | Safe-list ağı (Türk Telekom, Starlink, Google, Facebook, Proton…) engellenmiş | DERHAL bildir |
| g | Pazartesi | Haftalık özet: 7g trend, eklenen ağlar, açık inceleme, kural sayıları |

Bunların hiçbiri yoksa: sessizce bit.

## Güvenlik

- Datacamp ve M247 için hard engel görürsen LOUD uyar; kendin düzeltme.
- Geri alma: Worker’ı dry-run’a almak yalnızca **yeni** eklemeleri durdurur; eskiyi geri almaz. Silme elle, Cloudflare panosundan.
- Aynı sweep’i ikinci bir yerde koşturma (ruleset yarışı).
- `WORKER_SECRET` / Cloudflare / Shopify sırlarını asla commit etme.

## Çıktı kanalı

1. **Bu agent sohbeti** — kısa Türkçe rapor (yalnız tetikleyici varsa). E-posta yok.
2. Dropbox arşivi (tetikleyici varsa):  
   `/@ Claude/STORE_SYSTEMS/Bot Defense/reports/YYYY-MM-DD.md`

Sakin günde sohbete de yazma; Dropbox’a da yazma.
