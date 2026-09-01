/** Pure helpers for gorgias-proxy. Keep behavior aligned with production v1.1-gorgias-2026-08-19. */

export const VERSION = "v1.1-gorgias-2026-08-19";

export function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const enc = new TextEncoder();
  const ab = enc.encode(a);
  const bb = enc.encode(b);
  if (ab.length !== bb.length) return false;
  let diff = 0;
  for (let i = 0; i < ab.length; i++) diff |= ab[i] ^ bb[i];
  return diff === 0;
}

export function authorized(request, env) {
  const h = request.headers.get("authorization") || "";
  const m = /^Bearer\s+(.+)$/i.exec(h.trim());
  if (!m) return false;
  return timingSafeEqual(m[1].trim(), env.WORKER_SECRET || "");
}

export function customerAddress(ticket) {
  if (!ticket) return null;
  if (ticket.customer && ticket.customer.email) return ticket.customer.email;
  if (Array.isArray(ticket.receiver) && ticket.receiver[0] && ticket.receiver[0].email) {
    return ticket.receiver[0].email;
  }
  return null;
}

export function checkExpectations(ticket, payload, idFromPath) {
  const mismatches = [];
  if (payload.expect_ticket_id !== undefined && Number(payload.expect_ticket_id) !== Number(idFromPath)) {
    mismatches.push({
      field: "ticket_id",
      expected: Number(payload.expect_ticket_id),
      actual: Number(idFromPath),
    });
  }
  if (payload.expect_customer_email !== undefined) {
    const actual = (customerAddress(ticket) || "").trim().toLowerCase();
    const expected = String(payload.expect_customer_email).trim().toLowerCase();
    if (!actual || actual !== expected) {
      mismatches.push({ field: "customer_email", expected, actual: actual || null });
    }
  }
  if (!mismatches.length) return null;
  return {
    ok: false,
    error: "expectation_mismatch",
    detail: "Beklenen kimlik ticket ile uyusmuyor - mesaj GONDERILMEDI.",
    mismatches,
    version: VERSION,
  };
}

export function stripHtml(s) {
  return String(s)
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n\n")
    .replace(/<[^>]+>/g, "")
    .trim();
}

export function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function buildMessage(env, ticket, payload, channel) {
  const senderId = Number(payload.sender_id ?? env.BOT_USER_ID);
  if (!senderId) throw new Error("missing_sender: set BOT_USER_ID or pass sender_id");
  const bodyText = payload.body_text ?? stripHtml(payload.body_html || "");
  const bodyHtml = payload.body_html ?? escapeHtml(payload.body_text || "").replace(/\n/g, "<br>");
  if (!bodyText.trim() && !payload.body_html) {
    throw new Error("missing_body: provide body_text or body_html");
  }
  const msg = {
    channel,
    via: "api",
    from_agent: true,
    sender: { id: senderId },
    body_text: bodyText,
    body_html: bodyHtml,
  };
  if (channel === "email") {
    const fromAddress = payload.from_address || env.BOT_FROM_ADDRESS;
    if (!fromAddress) throw new Error("missing_from_address: set BOT_FROM_ADDRESS");
    const toAddress = payload.to_address || customerAddress(ticket);
    if (!toAddress) throw new Error("missing_to_address: pass to_address");
    msg.subject = payload.subject || `Re: ${ticket && ticket.subject ? ticket.subject : "your message"}`;
    msg.source = {
      type: "email",
      to: [{ address: toAddress, name: payload.to_name || undefined }],
      from: { address: fromAddress, name: payload.from_name || env.BOT_FROM_NAME || undefined },
    };
  }
  return msg;
}

export function attachmentUrlAllowed(target) {
  let u;
  try {
    u = new URL(target);
  } catch {
    return { ok: false, error: "bad_url" };
  }
  const hostOk = u.protocol === "https:" && /(^|\.)gorgias\.(io|com)$/.test(u.hostname);
  if (!hostOk) return { ok: false, error: "host_not_allowed" };
  return { ok: true, url: u };
}

export function matchRoute(method, path) {
  const seg = path.split("/").filter(Boolean);
  if (path === "/health" || path === "/") return { name: "health" };
  if (path === "/dry-run" && method === "GET") return { name: "dry-run" };
  if (seg[0] === "tickets" && seg.length === 1 && method === "GET") return { name: "tickets-list" };
  if (seg[0] === "tickets" && seg.length >= 2) {
    const id = seg[1];
    const sub = seg[2];
    if (!sub && method === "GET") return { name: "ticket-get", id };
    if (sub === "messages" && method === "GET") return { name: "messages", id };
    if ((sub === "reply" || sub === "note") && method === "POST") return { name: sub, id };
    if (sub === "assign" && method === "POST") return { name: "assign", id };
    if (sub === "unassign" && method === "POST") return { name: "unassign", id };
    if (sub === "tags" && (method === "POST" || method === "DELETE")) return { name: "tags", id };
    if ((sub === "close" || sub === "reopen") && method === "POST") return { name: sub, id };
  }
  if (seg[0] === "attachment" && seg.length === 1 && method === "GET") return { name: "attachment" };
  if (seg[0] === "views" && seg.length === 1 && method === "GET") return { name: "views" };
  if (seg[0] === "users" && seg.length === 1 && method === "GET") return { name: "users" };
  return { name: "not_found" };
}
