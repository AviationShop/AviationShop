# Gap watchdog

Ayrı Cursor Automation, **saat başı**. Publisher 6×4s slot sonrası eşik **5.0 saat** (eski 7.0).

## ADIM 1

Shopify News son 5 makale `sortKey: PUBLISHED_AT, reverse:true`. En yeninin UTC yaşı ≤5.0h → `watchdog OK`, DUR.

## ADIM 1b — slot testi

Slotlar TR 00/04/08/12/16/20. Son geçmiş slottan ~90 dk içinde ≥1 makale yoksa `publisher_runlog` oku: `IN_PROGRESS` kalmışsa `runlog_stopped_at`, kayıt yoksa `runlog_missing: yes`.

## ADIM 1c

Sonraki slota <45 dk → catch-up yok.

## ADIM 2–3

Taze allow yoksa `real_lull`. Varsa publisher deep-run, aynı kalite kapıları. Taze allow varken 0 yayın → `🔴 SILENT-FAIL`.

Catch-up ledger alanları publisher ile birebir. `handle`/`badge` patch edilemez — bozuk satır: yedek → `/story-delete` → tam `/ledger-add`. Shopify makalesine dokunma.

API 529/503/5xx: 60s × max 3.
