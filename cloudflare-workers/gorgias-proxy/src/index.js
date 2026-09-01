/**
 * gorgias-proxy — Bearer token in, Gorgias Basic Auth out.
 * Route whitelist + expect_* gate on public replies.
 * Behavior matches production Worker v1.1-gorgias-2026-08-19.
 *
 * Secrets (wrangler secret put — never commit):
 *   WORKER_SECRET, GORGIAS_API_KEY, GORGIAS_EMAIL, GORGIAS_DOMAIN
 * Optional vars: GORGIAS_VIEW_ID, BOT_USER_ID, BOT_FROM_ADDRESS, BOT_FROM_NAME
 */
import {
  VERSION,
  authorized,
  checkExpectations,
  buildMessage,
  attachmentUrlAllowed,
} from "./lib.js";

function json(obj, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...extraHeaders },
  });
}

function fail(status, error, detail, extraHeaders = {}) {
  return json({ ok: false, error, detail: detail ?? null, version: VERSION }, status, extraHeaders);
}

function scrub(text, env) {
  if (typeof text !== "string") {
    try {
      text = JSON.stringify(text);
    } catch {
      text = String(text);
    }
  }
  const secrets = [env.GORGIAS_API_KEY, env.WORKER_SECRET].filter(Boolean);
  for (const s of secrets) {
    if (!s) continue;
    text = text.split(s).join("[REDACTED]");
    try {
      const b64 = btoa(`${env.GORGIAS_EMAIL}:${s}`);
      text = text.split(b64).join("[REDACTED]");
      text = text.split(btoa(s)).join("[REDACTED]");
    } catch {
      /* ignore */
    }
  }
  return text;
}

async function gorgias(env, method, path, body) {
  const base = (env.GORGIAS_DOMAIN || "").replace(/\/+$/, "");
  const url = `${base}${path}`;
  const auth = btoa(`${env.GORGIAS_EMAIL}:${env.GORGIAS_API_KEY}`);
  let res;
  try {
    res = await fetch(url, {
      method,
      headers: {
        authorization: `Basic ${auth}`,
        accept: "application/json",
        ...(body !== undefined ? { "content-type": "application/json" } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    return {
      ok: false,
      status: 502,
      data: { ok: false, error: "gorgias_unreachable", detail: scrub(String(e && e.message), env) },
      headers: {},
    };
  }
  const raw = await res.text();
  let data;
  try {
    data = raw ? JSON.parse(raw) : null;
  } catch {
    data = { raw: scrub(raw, env) };
  }
  const headers = {};
  const ra = res.headers.get("retry-after");
  if (ra) headers["retry-after"] = ra;
  const rl = res.headers.get("x-gorgias-account-api-call-limit");
  if (rl) headers["x-gorgias-rate-limit"] = rl;
  if (!res.ok) {
    const scrubbed = JSON.parse(scrub(JSON.stringify(data ?? {}), env));
    return {
      ok: false,
      status: res.status,
      data: {
        ok: false,
        error: res.status === 429 ? "gorgias_rate_limited" : "gorgias_error",
        gorgias_status: res.status,
        gorgias_body: scrubbed,
        retry_after: ra || null,
        version: VERSION,
      },
      headers,
    };
  }
  return { ok: true, status: res.status, data, headers };
}

function passthrough(r, shape) {
  if (!r.ok) return json(r.data, r.status, r.headers);
  return json({ ok: true, version: VERSION, ...(shape ? shape(r.data) : { data: r.data }) }, 200, r.headers);
}

async function readJson(request) {
  const txt = await request.text();
  if (!txt.trim()) return {};
  return JSON.parse(txt);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const method = request.method.toUpperCase();

    if (path === "/health" || path === "/") {
      return json({
        ok: true,
        service: "gorgias-proxy",
        version: VERSION,
        gorgias_domain: env.GORGIAS_DOMAIN || null,
        configured: {
          gorgias_api_key: Boolean(env.GORGIAS_API_KEY),
          worker_secret: Boolean(env.WORKER_SECRET),
          default_view_id: env.GORGIAS_VIEW_ID || null,
          bot_user_id: env.BOT_USER_ID || null,
          bot_from_address: env.BOT_FROM_ADDRESS || null,
        },
      });
    }

    if (path === "/dry-run" && method === "GET") {
      const viewId = url.searchParams.get("view_id") || env.GORGIAS_VIEW_ID;
      if (!viewId) return fail(400, "missing_view_id", "GORGIAS_VIEW_ID is not configured");
      const r = await gorgias(
        env,
        "GET",
        `/views/${encodeURIComponent(viewId)}/items?limit=30&order_by=updated_datetime:desc`
      );
      if (!r.ok) return json(r.data, r.status, r.headers);
      const items = Array.isArray(r.data && r.data.data) ? r.data.data : [];
      const summary = { open: 0, closed: 0, other: 0, assigned: 0, unassigned: 0 };
      for (const t of items) {
        const s = t && t.status;
        if (s === "open") summary.open++;
        else if (s === "closed") summary.closed++;
        else summary.other++;
        if (t && t.assignee_user) summary.assigned++;
        else summary.unassigned++;
      }
      return json({
        ok: true,
        mode: "dry-run",
        version: VERSION,
        view_id: viewId,
        inspected: items.length,
        summary,
        actions_performed: { reply: 0, assign: 0, tag: 0, close: 0 },
        note: "No customer content returned; no mutation performed.",
      });
    }

    if (!authorized(request, env)) {
      return fail(401, "unauthorized", "Missing or invalid Authorization: Bearer <WORKER_SECRET>");
    }
    if (!env.GORGIAS_API_KEY) return fail(500, "not_configured", "GORGIAS_API_KEY secret is not set");

    try {
      const seg = path.split("/").filter(Boolean);

      if (seg[0] === "tickets" && seg.length === 1 && method === "GET") {
        const viewId = url.searchParams.get("view_id") || env.GORGIAS_VIEW_ID;
        if (!viewId) {
          return fail(400, "missing_view_id", "Create a saved View in Gorgias, then set GORGIAS_VIEW_ID or pass ?view_id=");
        }
        const limit = url.searchParams.get("limit") || "30";
        const cursor = url.searchParams.get("cursor");
        const order = url.searchParams.get("order_by") || "updated_datetime:desc";
        const qs = new URLSearchParams({ limit, order_by: order });
        if (cursor) qs.set("cursor", cursor);
        const r = await gorgias(env, "GET", `/views/${encodeURIComponent(viewId)}/items?${qs}`);
        return passthrough(r, (d) => ({
          view_id: viewId,
          count: Array.isArray(d && d.data) ? d.data.length : null,
          next_cursor: (d && d.meta && d.meta.next_cursor) || null,
          tickets: (d && d.data) || [],
        }));
      }

      if (seg[0] === "tickets" && seg.length >= 2) {
        const id = encodeURIComponent(seg[1]);
        const sub = seg[2];

        if (!sub && method === "GET") {
          const r = await gorgias(env, "GET", `/tickets/${id}`);
          return passthrough(r, (d) => ({ ticket: d }));
        }

        if (sub === "messages" && method === "GET") {
          const limit = url.searchParams.get("limit") || "30";
          const r = await gorgias(env, "GET", `/tickets/${id}/messages?limit=${encodeURIComponent(limit)}`);
          return passthrough(r, (d) => ({
            count: Array.isArray(d && d.data) ? d.data.length : null,
            messages: (d && d.data) || [],
          }));
        }

        if ((sub === "reply" || sub === "note") && method === "POST") {
          const payload = await readJson(request);
          const channel = sub === "reply" ? "email" : "internal-note";
          let ticket = null;
          if (channel === "email") {
            const t = await gorgias(env, "GET", `/tickets/${id}`);
            if (!t.ok) return json(t.data, t.status, t.headers);
            ticket = t.data;
          }
          const guard = checkExpectations(ticket, payload, id);
          if (guard) return json(guard, 409);
          let msg;
          try {
            msg = buildMessage(env, ticket, payload, channel);
          } catch (e) {
            const [code, ...rest] = String(e.message).split(": ");
            return fail(400, code, rest.join(": ") || null);
          }
          const r = await gorgias(env, "POST", `/tickets/${id}/messages`, msg);
          return passthrough(r, (d) => ({
            sent: true,
            channel,
            requested_ticket_id: Number(seg[1]),
            ticket_id: (d && d.ticket_id) ?? null,
            to_address: (msg.source && msg.source.to && msg.source.to[0] && msg.source.to[0].address) || null,
            message_id: d && d.id,
            message: d,
          }));
        }

        if (sub === "assign" && method === "POST") {
          const payload = await readJson(request);
          const userId = Number(payload.assignee_user_id ?? payload.user_id ?? env.BOT_USER_ID);
          if (!userId) return fail(400, "missing_assignee_user_id", "Pass assignee_user_id");
          const r = await gorgias(env, "PUT", `/tickets/${id}`, { assignee_user: { id: userId } });
          return passthrough(r, (d) => ({ assigned_to: userId, ticket: d }));
        }

        if (sub === "unassign" && method === "POST") {
          const r = await gorgias(env, "PUT", `/tickets/${id}`, { assignee_user: null });
          return passthrough(r, (d) => ({ assigned_to: null, ticket: d }));
        }

        if (sub === "tags" && (method === "POST" || method === "DELETE")) {
          const payload = await readJson(request);
          const tags = (Array.isArray(payload.tags) ? payload.tags : [payload.tag]).filter(Boolean);
          if (!tags.length) return fail(400, "missing_tags", 'Pass {"tags":["name",...]}');
          const names = tags.filter((t) => typeof t !== "number").map((t) => String(t));
          const ids = tags.filter((t) => typeof t === "number");
          const body = {};
          if (names.length) body.names = names;
          if (ids.length) body.ids = ids;
          const r = await gorgias(env, method, `/tickets/${id}/tags`, body);
          return passthrough(r, (d) => ({ action: method === "POST" ? "added" : "removed", tags, result: d }));
        }

        if ((sub === "close" || sub === "reopen") && method === "POST") {
          const status = sub === "close" ? "closed" : "open";
          const r = await gorgias(env, "PUT", `/tickets/${id}`, { status });
          return passthrough(r, (d) => ({ status, ticket: d }));
        }
      }

      if (seg[0] === "attachment" && seg.length === 1 && method === "GET") {
        const target = url.searchParams.get("url");
        if (!target) return fail(400, "missing_url", "Pass ?url=<attachment url>");
        const allowed = attachmentUrlAllowed(target);
        if (!allowed.ok) {
          return fail(
            400,
            allowed.error,
            allowed.error === "bad_url" ? "Gecerli bir URL degil" : "Sadece https://*.gorgias.io ve *.gorgias.com"
          );
        }
        let u = allowed.url;
        if (u.hostname === "uploads.gorgias.io") {
          const base = (env.GORGIAS_DOMAIN || "").replace(/\/+$/, "");
          u = new URL(`${base}/attachment/download${u.pathname}`);
        }
        const auth = btoa(`${env.GORGIAS_EMAIL}:${env.GORGIAS_API_KEY}`);
        let res;
        try {
          res = await fetch(u.toString(), {
            headers: { authorization: `Basic ${auth}`, accept: "*/*" },
            redirect: "follow",
          });
        } catch (e) {
          return fail(502, "fetch_failed", scrub(String(e && e.message), env));
        }
        const finalUrl = res.url || u.toString();
        if (/attachment_placeholder/.test(finalUrl)) {
          return fail(403, "attachment_forbidden", "Gorgias placeholder dondurdu: bu kimlikle eke erisilemiyor");
        }
        if (!res.ok) return fail(res.status, "attachment_error", `upstream ${res.status}`);
        return new Response(res.body, {
          status: 200,
          headers: {
            "content-type": res.headers.get("content-type") || "application/octet-stream",
            "content-length": res.headers.get("content-length") || "",
            "x-proxy-version": VERSION,
          },
        });
      }

      if (seg[0] === "views" && seg.length === 1 && method === "GET") {
        const r = await gorgias(env, "GET", `/views?limit=100`);
        return passthrough(r, (d) => ({
          views: ((d && d.data) || []).map((v) => ({ id: v.id, name: v.name, type: v.type })),
        }));
      }

      if (seg[0] === "users" && seg.length === 1 && method === "GET") {
        const r = await gorgias(env, "GET", `/users?limit=100`);
        return passthrough(r, (d) => ({
          users: ((d && d.data) || []).map((u) => ({
            id: u.id,
            name: u.name,
            email: u.email,
            active: u.active,
          })),
        }));
      }

      return fail(404, "not_found", `No route for ${method} ${path}`);
    } catch (e) {
      if (e instanceof SyntaxError) return fail(400, "bad_json", "Request body is not valid JSON");
      return fail(500, "worker_error", scrub(String(e && e.stack || e), env));
    }
  },
};
