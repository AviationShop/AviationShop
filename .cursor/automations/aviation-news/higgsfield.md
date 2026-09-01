# Higgsfield’i Cloud Agent ortamına bağlamak

Higgsfield bir **env secret değildir**. OAuth oturumudur. `CLOUDFLARE_API_TOKEN` / `SHOPIFY_*` kutusuna API key yapıştırılmaz; Higgsfield MCP anahtar vermez.

Bu ortam **kişisel / DB-managed**: [Cloud Agents environment](https://cursor.com/dashboard/cloud-agents/environments/e/6cb28dbd-a5dc-11f1-a7d1-d6b4613131ce). `environment.json` repo’da yok. MCP bağlantısı env snapshot’ından ayrıdır.

## Neden sende yeşil, bende 401?

İki ayrı şey:

| Ne | Nerede | Bu koşum (2026-09-01) |
| --- | --- | --- |
| MCP **sunucu kaydı** (araç listesi, yeşil nokta) | Desktop Cursor ve/veya [cursor.com/agents](https://cursor.com/agents) MCP menüsü | `ready` — araçlar görünüyor |
| Higgsfield **hesap oturumu** (üretim API’si) | Higgsfield’e OAuth | **expired** — `list_workspaces` 401 |

Bu koşumda `list_workspaces` hâlâ: *Your Higgsfield session has expired or is no longer valid.* Request ID `8659da59-f6f6-4fb9-b56a-84e9411b4d5f`.

Cursor yeşil = “Higgsfield MCP eklendi.” Higgsfield yeşil oturum = “bu agent senin kredinle üretebilir.” Desktop’ta bağlı görünmesi Cloud token’ını yenilemez. Cloud Agents MCP’yi masaüstü IDE’den bağımsız authorize eder ([Cursor docs](https://cursor.com/docs/cloud-agent/capabilities), [forum](https://forum.cursor.com/t/linear-access-failing-in-cloud-agents/166505)).

Repo `.cursor/mcp.json` yalnız URL taşır (`https://mcp.higgsfield.ai/mcp`). OAuth’u oluşturmaz.

## Bağla / yenile — bu link

**Cloud Agents MCP menüsü (asıl kapı):** [https://cursor.com/agents](https://cursor.com/agents)

Bu koşum: [https://cursor.com/agents/bc-9b968322-9f1f-42fa-a19b-0e1d43970dca](https://cursor.com/agents/bc-9b968322-9f1f-42fa-a19b-0e1d43970dca)

1. [cursor.com/agents](https://cursor.com/agents) aç (Desktop Settings değil).
2. Üstteki **MCP** menüsü → Higgsfield.
3. Yalnız Reconnect yetmezse: **Remove** → **Add / Enable**. Login ekranı açılmalı.
4. HTTP URL: `https://mcp.higgsfield.ai/mcp` ([higgsfield.ai/mcp](https://higgsfield.ai/mcp)).
5. Higgsfield hesabınla **Sign in / Authorize**. Callback: `https://www.cursor.com/agents/mcp/oauth/callback`.
6. Yeşil olunca **yeni** bir Cloud Agent / Automation başlat. **Bu koşum** eski 401 token’ı taşıyabilir; mevcut sohbet oturumu kendiliğinden düzelmez.
7. Smoke: agent `list_workspaces` → `is_selected` dolu workspace. O zaman yedek katman (`nano_banana_pro` 2k, gerçek 9:16/1:1) çalışır.

Takım paylaşımlı sunucu: Dashboard → **Integrations & MCP**. OAuth yine senin hesabın.

## Desktop (lokal Cursor)

Yedek / günlük IDE — Cloud’u doldurmaz:

1. Customize → Marketplace → Higgsfield → Add → login  
   veya `.cursor/mcp.json` (bu repoda URL hazır).
2. Redirect: masaüstü `http://localhost:8787/callback`.

## Pipeline’daki yeri (yedek)

Birincil görsel: Cursor **GenerateImage** (Grok Image 2). Higgsfield Cloud OAuth canlıysa yedek: `nano_banana_pro` / `grok_image_2_0` (3 aspect, native oran). 401 → `higgsfield_unavailable: yes` LOUD, hikâye düşmez.

Ayrıntı: `image-chain.md`.
