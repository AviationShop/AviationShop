import test from "node:test";
import assert from "node:assert/strict";
import {
  scanReplyBody,
  trackingUrl,
  emailsMatch,
  isStoreAddress,
  jacketSizeFromMeasures,
} from "./guards.js";

test("scanReplyBody blocks Shopify authenticate links", () => {
  const r = scanReplyBody(
    "Track here: https://www.aviationshop.com/123/orders/abc/authenticate?key=x"
  );
  assert.equal(r.ok, false);
  assert.ok(r.bad_tokens.includes("authenticate"));
});

test("scanReplyBody allows 17track links", () => {
  const r = scanReplyBody(
    "Tracking number: LX000000000CN\nhttps://www.17track.net/en/track#nums=LX000000000CN"
  );
  assert.equal(r.ok, true);
  assert.deepEqual(r.bad_tokens, []);
});

test("scanReplyBody blocks leftover placeholders", () => {
  const r = scanReplyBody("Send to <NINGBO_RETURN_ADDRESS>");
  assert.equal(r.ok, false);
  assert.deepEqual(r.placeholders, ["<NINGBO_RETURN_ADDRESS>"]);
});

test("trackingUrl builds only the 17track format", () => {
  assert.equal(
    trackingUrl("LX000000000CN"),
    "https://www.17track.net/en/track#nums=LX000000000CN"
  );
  assert.equal(trackingUrl("https://x.myshopify.com/orders/1"), null);
  assert.equal(trackingUrl(""), null);
});

test("emailsMatch is case-insensitive and rejects empty", () => {
  assert.equal(emailsMatch("A@Shop.com", "a@shop.com"), true);
  assert.equal(emailsMatch("", "a@shop.com"), false);
});

test("isStoreAddress recognizes support and orders", () => {
  const store = ["support@aviationshop.com", "orders@aviationshop.com"];
  assert.equal(isStoreAddress("Support@AviationShop.com", store), true);
  assert.equal(isStoreAddress("customer@example.com", store), false);
});

test("jacketSizeFromMeasures rounds up", () => {
  assert.equal(jacketSizeFromMeasures(50, 165), "S");
  assert.equal(jacketSizeFromMeasures(76, 176), "L");
  assert.equal(jacketSizeFromMeasures(96, 196), "XL");
});
