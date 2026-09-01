import test from "node:test";
import assert from "node:assert/strict";
import {
  VERSION,
  timingSafeEqual,
  authorized,
  checkExpectations,
  customerAddress,
  buildMessage,
  attachmentUrlAllowed,
  matchRoute,
} from "../src/lib.js";

test("timingSafeEqual rejects length mismatch and wrong bytes", () => {
  assert.equal(timingSafeEqual("abcd", "abcd"), true);
  assert.equal(timingSafeEqual("abcd", "abce"), false);
  assert.equal(timingSafeEqual("abcd", "abc"), false);
  assert.equal(timingSafeEqual(null, "x"), false);
});

test("authorized accepts Bearer token", () => {
  const env = { WORKER_SECRET: "s3cret" };
  const ok = new Request("https://proxy.test/tickets", {
    headers: { authorization: "Bearer s3cret" },
  });
  const bad = new Request("https://proxy.test/tickets", {
    headers: { authorization: "Bearer nope" },
  });
  const missing = new Request("https://proxy.test/tickets");
  assert.equal(authorized(ok, env), true);
  assert.equal(authorized(bad, env), false);
  assert.equal(authorized(missing, env), false);
});

test("checkExpectations returns 409 payload on ticket id mismatch", () => {
  const ticket = { customer: { email: "ornek.musteri@example.com" } };
  const guard = checkExpectations(ticket, { expect_ticket_id: 1, expect_customer_email: "ornek.musteri@example.com" }, 2);
  assert.equal(guard.error, "expectation_mismatch");
  assert.equal(guard.version, VERSION);
  assert.equal(guard.mismatches[0].field, "ticket_id");
});

test("checkExpectations returns 409 payload on email mismatch", () => {
  const ticket = { customer: { email: "a@example.com" } };
  const guard = checkExpectations(ticket, { expect_ticket_id: 9, expect_customer_email: "b@example.com" }, 9);
  assert.equal(guard.error, "expectation_mismatch");
  assert.equal(guard.mismatches[0].field, "customer_email");
});

test("checkExpectations passes when ids and emails match (case-insensitive)", () => {
  const ticket = { customer: { email: "A@Example.com" } };
  const guard = checkExpectations(
    ticket,
    { expect_ticket_id: 80, expect_customer_email: "a@example.com" },
    80
  );
  assert.equal(guard, null);
});

test("customerAddress reads customer.email then receiver", () => {
  assert.equal(customerAddress({ customer: { email: "c@x.com" } }), "c@x.com");
  assert.equal(customerAddress({ receiver: [{ email: "r@x.com" }] }), "r@x.com");
  assert.equal(customerAddress(null), null);
});

test("buildMessage sets email source.to from the ticket", () => {
  const msg = buildMessage(
    { BOT_USER_ID: "510914351", BOT_FROM_ADDRESS: "support@aviationshop.com" },
    { customer: { email: "ornek.musteri@example.com" }, subject: "Order" },
    { body_text: "Dear Customer,\nHello." },
    "email"
  );
  assert.equal(msg.from_agent, true);
  assert.equal(msg.channel, "email");
  assert.equal(msg.source.to[0].address, "ornek.musteri@example.com");
  assert.equal(msg.source.from.address, "support@aviationshop.com");
});

test("buildMessage refuses empty body", () => {
  assert.throws(
    () => buildMessage({ BOT_USER_ID: 1, BOT_FROM_ADDRESS: "a@b.c" }, { customer: { email: "c@d.e" } }, {}, "email"),
    /missing_body/
  );
});

test("attachmentUrlAllowed only allows gorgias hosts over https", () => {
  assert.equal(attachmentUrlAllowed("https://uploads.gorgias.io/x").ok, true);
  assert.equal(attachmentUrlAllowed("https://aviation-shop.gorgias.com/a").ok, true);
  assert.equal(attachmentUrlAllowed("https://evil.example/a").ok, false);
  assert.equal(attachmentUrlAllowed("http://uploads.gorgias.io/x").ok, false);
  assert.equal(attachmentUrlAllowed("not a url").error, "bad_url");
});

test("matchRoute whitelist: tickets create is not_found; reply/note/close exist", () => {
  assert.equal(matchRoute("POST", "/tickets").name, "not_found");
  assert.equal(matchRoute("POST", "/tickets/1/reply").name, "reply");
  assert.equal(matchRoute("POST", "/tickets/1/note").name, "note");
  assert.equal(matchRoute("POST", "/tickets/1/close").name, "close");
  assert.equal(matchRoute("GET", "/tickets?view_id=1").name, "not_found");
  assert.equal(matchRoute("GET", "/tickets").name, "tickets-list");
  assert.equal(matchRoute("GET", "/health").name, "health");
  assert.equal(matchRoute("GET", "/users").name, "users");
});
