/**
 * Reply-body guards for Aviation Claude.
 * No network. No secrets. Import from tests or run with: node --test
 */

const FORBIDDEN = ["authenticate", "myshopify", "/admin"];

export function scanReplyBody(body) {
  const text = String(body ?? "");
  const lower = text.toLowerCase();
  const hits = FORBIDDEN.filter((token) => lower.includes(token));
  const placeholders = [...text.matchAll(/<[A-Z0-9_]+>/g)].map((m) => m[0]);
  return {
    ok: hits.length === 0 && placeholders.length === 0,
    bad_tokens: hits,
    placeholders,
  };
}

export function trackingUrl(trackingNumber) {
  const num = String(trackingNumber ?? "").trim();
  if (!num) return null;
  if (/authenticate|myshopify|\/admin/i.test(num)) return null;
  return `https://www.17track.net/en/track#nums=${encodeURIComponent(num)}`;
}

export function emailsMatch(expected, actual) {
  const a = String(expected ?? "").trim().toLowerCase();
  const b = String(actual ?? "").trim().toLowerCase();
  return Boolean(a) && Boolean(b) && a === b;
}

export function isStoreAddress(email, storeAddresses) {
  const needle = String(email ?? "").trim().toLowerCase();
  return storeAddresses.some((addr) => String(addr).trim().toLowerCase() === needle);
}

export function jacketSizeFromMeasures(kg, cm) {
  const rows = [
    { size: "S", kg: 50, cm: 165 },
    { size: "M", kg: 75, cm: 175 },
    { size: "L", kg: 85, cm: 185 },
    { size: "XL", kg: 95, cm: 195 },
  ];
  if (!Number.isFinite(kg) && !Number.isFinite(cm)) return null;
  const scored = rows.map((row) => {
    const dk = Number.isFinite(kg) ? kg / row.kg : 0;
    const dc = Number.isFinite(cm) ? cm / row.cm : 0;
    const ratio = Math.max(dk, dc, Number.isFinite(kg) ? dk : dc);
    return { ...row, ratio };
  });
  const fit = scored.find((row) => row.ratio <= 1) ?? scored[scored.length - 1];
  return fit.size;
}
