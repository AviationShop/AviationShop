# gorgias-proxy

Cloudflare Worker between Aviation Claude and Gorgias.

- Session → Worker: `Authorization: Bearer <WORKER_SECRET>`
- Worker → Gorgias: HTTP Basic `GORGIAS_EMAIL:GORGIAS_API_KEY`
- `POST /tickets` is **not** routed (bot cannot create tickets)
- `POST /tickets/:id/reply` requires `expect_ticket_id` / `expect_customer_email` when sent; mismatch → **409** `expectation_mismatch` and the message is not sent
- Success body includes `sent: true`, `requested_ticket_id`, `to_address`

Live: `https://gorgias-proxy.oevitan.workers.dev` · version `v1.1-gorgias-2026-08-19`  
This folder is a **source copy** of that Worker. Do not `wrangler deploy` from an inbox run. Production already has secrets and is serving traffic.

## Secrets (names only)

```
wrangler secret put WORKER_SECRET
wrangler secret put GORGIAS_API_KEY
wrangler secret put GORGIAS_EMAIL
wrangler secret put GORGIAS_DOMAIN
```

`GORGIAS_DOMAIN` is the API root including `/api` (example shape: `https://<account>.gorgias.com/api`).  
Vars in `wrangler.jsonc` are non-secret: Unassigned view, bot user id, `support@aviationshop.com`.

Local secret file (chmod 600, never echo):

```
mkdir -p ~/cloudflare-workers/gorgias-proxy
# paste WORKER_SECRET with an editor — do not echo (shell history)
chmod 600 ~/cloudflare-workers/gorgias-proxy/WORKER_SECRET.txt
```

## Tests

```
node --test test/*.test.js
```

## Health

`GET /health` is unauthenticated and only returns booleans + configured view/bot ids. Use it to confirm the Worker is up. Do not treat it as a credential check.
