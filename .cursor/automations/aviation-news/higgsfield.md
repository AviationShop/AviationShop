# Higgsfield’i Cloud Agent ortamına bağlamak

Higgsfield bir **env secret değildir**. OAuth oturumudur. `CLOUDFLARE_API_TOKEN` / `SHOPIFY_*` kutusuna API key yapıştırılmaz; Higgsfield MCP anahtar vermez.

Bu ortam **kişisel / DB-managed**: [Cloud Agents environment](https://cursor.com/dashboard/cloud-agents/environments/e/6cb28dbd-a5dc-11f1-a7d1-d6b4613131ce). `environment.json` repo’da yok. MCP bağlantısı env snapshot’ından ayrıdır.

## Bu ekranda ayar yok (Onur, 2026-09-01)

Cursor Desktop → **Automations** → AviationShop dashboard (**Ask Cursor…**, `@ AVIATION NEWS PUBLISHER` kartları) Higgsfield / MCP menüsü **içermez**. Environment sayfası da içermez. Eski “üstte MCP dropdown” metni güncel UI ile uyuşmuyor ([forum](https://forum.cursor.com/t/unclear-how-to-add-mcp-to-cloud-env/166993)).

## Neden sende yeşil, bende 401?

İki ayrı şey:

| Ne | Nerede | Bu koşum |
| --- | --- | --- |
| MCP **sunucu kaydı** (araç listesi) | Desktop Customize MCP ve/veya Cloud `+` menüsü | `ready` — araçlar görünüyor |
| Higgsfield **hesap oturumu** | Higgsfield OAuth | **expired** — `list_workspaces` 401 |

Desktop yeşil = laptop agent. Cloud yeşil oturum = bu VM senin kredinle üretir. Aynı değil.

Repo `.cursor/mcp.json` yalnız URL taşır (`https://mcp.higgsfield.ai/mcp`). OAuth’u oluşturmaz.

## Bağla — tarayıcı, Desktop Automations değil

**1) Cloud Agents (bu koşumun kapısı)** — [https://cursor.com/agents](https://cursor.com/agents)

Bu koşum: [https://cursor.com/agents/bc-9b968322-9f1f-42fa-a19b-0e1d43970dca](https://cursor.com/agents/bc-9b968322-9f1f-42fa-a19b-0e1d43970dca)

1. Linki **tarayıcıda** aç (Cursor Desktop → Automations değil).
2. Prompt çubuğunun **solundaki `+`** (model seçicinin yanında: files / skills / MCP).
3. **MCP Servers** → Higgsfield. Yoksa alta **Add MCP** → `https://mcp.higgsfield.ai/mcp`.
4. **Authenticate / Sign in**. Callback: `https://www.cursor.com/agents/mcp/oauth/callback`.
5. Yeşil olunca **yeni** Cloud Agent başlat. Bu sohbet eski 401 token’ı taşıyabilir.

**2) Automation Tools (cron yedek)** — [https://cursor.com/automations](https://cursor.com/automations)

Aviation News otomasyonunu aç → **Tools** → **MCP server** → Higgsfield Authenticate. Desktop Automations listesi değil; `cursor.com/automations` editörü. ([docs](https://cursor.com/docs/cloud-agent/automations))

Higgsfield ürün sayfası: [https://higgsfield.ai/mcp](https://higgsfield.ai/mcp).

Smoke: yeni koşumda `list_workspaces` → `is_selected` dolu. O zaman `nano_banana_pro` 2k yedek (native 9:16/1:1) açılır.

Takım paylaşımlı: Dashboard → **Integrations & MCP**. OAuth yine senin hesabın (Team Owned otomasyon = service account, ayrı).

## Desktop (lokal Cursor)

Customize → MCP / Marketplace → Higgsfield. Redirect: `http://localhost:8787/callback`. Cloud’u doldurmaz.

## Pipeline’daki yeri (yedek)

Birincil görsel: Cursor **GenerateImage** (Grok Image 2). Higgsfield Cloud OAuth canlıysa yedek: `nano_banana_pro` / `grok_image_2_0`. 401 → `higgsfield_unavailable: yes` LOUD, hikâye düşmez.

Ayrıntı: `image-chain.md`.
