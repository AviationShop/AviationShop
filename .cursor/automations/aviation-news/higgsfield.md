# Higgsfield’i Cloud Agent ortamına bağlamak

Higgsfield bir **env secret değildir**. OAuth oturumudur. `CLOUDFLARE_API_TOKEN` / `SHOPIFY_*` kutusuna API key yapıştırılmaz; Higgsfield MCP anahtar vermez.

Bu ortam **kişisel / DB-managed**: [Cloud Agents environment](https://cursor.com/dashboard/cloud-agents/environments/e/6cb28dbd-a5dc-11f1-a7d1-d6b4613131ce). `environment.json` repo’da yok. MCP bağlantısı env snapshot’ından ayrıdır.

2026-09-01 bu koşuda `list_workspaces` → **401 session expired**. Desktop’ta yeşil görünmesi Cloud’u otomatik doldurmaz.

## Cloud (otomasyon + bu agent) — asıl adım

Cursor dokümantasyonu: Cloud Agents, takım/kişisel MCP sunucularını **cursor.com/agents** üzerinden kullanır. OAuth **kullanıcı başına**.

1. [cursor.com/agents](https://cursor.com/agents) aç.
2. Üstteki **MCP** menüsü → Higgsfield’i **Add / Enable**.
3. URL (HTTP, stdio değil): `https://mcp.higgsfield.ai/mcp`
4. Higgsfield hesabınla **Sign in / Authorize**. Ücretli Higgsfield kredisi gerekir.
5. Yeşil olunca yeni bir Cloud Agent / Automation başlat (mevcut koşum eski 401 token’ı taşıyabilir).
6. Smoke: agent `list_workspaces` çağırsın. `is_selected` dolu workspace dönmeli.

Oturum düştüyse: MCP menüsünden **Remove** → tekrar Add. Yalnız “reconnect” bazen login ekranını açmaz.

Takım paylaşımlı sunucu: Dashboard → **Integrations & MCP**. OAuth yine senin hesabın.

## Desktop (lokal Cursor)

Yedek / günlük IDE için:

1. Customize → Marketplace → Higgsfield → Add → login  
   veya `.cursor/mcp.json` (bu repoda URL hazır).
2. Redirect: masaüstü `http://localhost:8787/callback`, web/cloud `https://www.cursor.com/agents/mcp/oauth/callback`.

Bu dosya Cloud OAuth’unu **oluşturmaz**. Cloud için yine agents MCP menüsü.

## Pipeline’daki yeri (yedek)

Birincil görsel: Cursor **GenerateImage** (Grok Image 2). Higgsfield bağlıysa yedek katman: `grok_image_2_0` (3 aspect). Yoksa yayın durmaz.

Ayrıntı: `image-chain.md`.
