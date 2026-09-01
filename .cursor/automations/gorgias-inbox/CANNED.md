# §CANNED — Onur-approved reply library

These templates are used **verbatim in meaning**. Do not add amounts, dates, refund promises, or extra process.

- Customer language: reply in the customer's language. If unsure, English.
- Always append [§İMZA](#imza).
- Greeting: `Dear <FirstName>,` only if that name came from **this** ticket. Otherwise `Dear Customer,`.
- Run `lib/guards.js` `scanReplyBody` on the finished body. If `ok` is false → do not send.
- Angle-bracket tokens like `<NINGBO_RETURN_ADDRESS>` are **not** customer text. If any remain, do not send that template.

Source: Gorgias playbook v4.1 (31 Aug 2026). T5 is the exact ack from that document. T1–T4 and T6–T10 are rebuilt from the same numbered constraints. If Onur pastes a live original over a template, the pasted text wins.

## İmza

```
Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

Never show Gmail connector addresses, Onur's personal address, or Kalvin's address to the customer.

---

## T1 — Return address (Rule 14 · Rule 15 stage 2)

Ticket: **CLOSE**. Tag `RETURN/EXCHANGE`. Assign Kalvin. No note. Do **not** add an amount, approval, or extra deadline beyond the four conditions below.

If `<NINGBO_RETURN_ADDRESS>` is still in the body → **do not send T1**. T5 + Kalvin + leave open + `NOTE for Onur: T1 street address missing from CANNED.md`.

```
Dear Customer,

You can return the item to our warehouse in Ningbo, Zhejiang, China:

<NINGBO_RETURN_ADDRESS>

Please read these conditions carefully before you ship:

1. Return shipping is paid by the customer. Expect about $45–$65 depending on your carrier and country.
2. Use a trackable / registered service only.
3. The parcel must be shipped within 30 days of delivery.
4. Custom / personalized items cannot be returned or exchanged.

On the customs form, do not declare a value above $20. A higher declaration can trigger a 100% tariff in China and the parcel may be refused.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T2 — Wrong size after delivery (Rule 15 stage 1)

Ticket: **OPEN**. Tag `RETURN/EXCHANGE`. Assign Kalvin. Short note.

```
Dear Customer,

Sorry the size did not work out. You have two options:

1. Return the item. Return shipping is paid by the customer (about $35–$65) using a trackable service.
2. Keep the item you have and order the new size at 30% off. Our team will send the discount code.

Each product has its own size chart under the product title / in the description. Please check that chart before you choose the new size.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T3 — Size chart / measurements before purchase (Rule 7B when no measurements)

Ticket: **OPEN**. Assign Kalvin. Short note. The bot does **not** recommend a size here.

```
Dear Customer,

To help with sizing, please send:

- Height
- Weight
- Chest
- Waist
- Shoulder width
- Sleeve length

You can order now and send the measurements afterwards — we can adjust before production — or wait until you have checked the size chart on the product page.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T4 — Damaged / wrong item — ask for proof (Rule 13 stage 1)

Ticket: **CLOSE**. No assign. No note. When the customer sends photos the ticket reopens into stage 2.

```
Dear Customer,

We are sorry the item arrived damaged or incorrect. Please reply to this email with clear photos or a short video of:

- The item
- The issue
- The packaging if it is relevant

Once we have that, our team will review it and get back to you.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T5 — Handover ACK (exact text from v4.1)

Ticket: **OPEN**. Used only when a human will actually reply. No money / return / date promises.

```
Dear Customer,

Thank you for sending this over. We have received your message and the details you provided.

Our team will review everything carefully and get back to you shortly.

Thank you for your patience.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T6 — Wholesale / B2B (Rule 16)

Ticket: **CLOSE**. No assign. No note. No price, discount, or minimum-quantity promise.

```
Dear Customer,

We supply 120+ stores. To get a wholesale quote:

1. Create an account on aviationshop.com
2. Add the products to your cart (colour + quantity)
3. Go to checkout, then leave without paying
4. When the cart reaches our system we prepare a custom price offer
5. Payment is by credit card, PayPal, or bank transfer (USD, EUR, or GBP)

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T7 — Custom name / personalization received (Rule 4B-1 · §CUSTOM-NAME)

Ticket: **OPEN**. Assign Kalvin unless already assigned — then **do not change** assignment. Short note with the name **exactly as written**. No “we will get back to you.” No date.

If the same message also asks a question → send **T5** instead and put the question in the note.

```
Dear Customer,

Thank you. We have received your personalization details and passed them to production.

Nothing else is needed from you for the name / custom text.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T8 — Production & shipping window

Prep 3–7 business days, then 7–15 days after dispatch. No specific calendar date. If the order is fulfilled **and** a tracking number exists → use **T9**, not T8.

```
Dear Customer,

Custom / made-to-order items are prepared in 3–7 business days. After the parcel is handed to the carrier, delivery is usually 7–15 days.

Your tracking number will be emailed to you once the order ships.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

---

## T9 — Tracking (Rule 11 fulfilled + number)

Ticket: **CLOSE**. Tracking number comes only from Shopify fulfillment. Link format is mandatory.

```
Dear Customer,

Order: #<ORDER_NO>
Tracking number: <TRACKING_NO>
Tracking link: https://www.17track.net/en/track#nums=<TRACKING_NO>

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

Replace `<ORDER_NO>` and `<TRACKING_NO>` with Shopify values before send. If either is missing, do not send T9.

---

## T10 — Custom-design product exists (§CUSTOM-KATALOG)

Ticket: **CLOSE**. No Kalvin handover. No price, production time, mockup, or “we will send a design first.”

```
Dear Customer,

We do not have a ready-made <DESIGN> <PRODUCT_TYPE> in the catalog, but we do produce this item as a custom design.

You can order it here:
https://www.aviationshop.com<VERIFIED_CUSTOM_PATH>

Add the logo / image / airline you want in the checkout note or personalization field.

Kind regards,
Aviation Claude
support@aviationshop.com | Customer Support
```

`<VERIFIED_CUSTOM_PATH>` must be a handle you just confirmed via product JSON or Shopify search. Do not invent a path.

Verified catalog shortcuts (still confirm before send):

| Type | Path |
| --- | --- |
| Pillow | `/products/custom-design-image-logo-designed-airplane-shape-decorative-pillows` |
| Hat | `/products/custom-design-image-hats` |
| Hoodie | `/products/concorde-designed-huawei-honor-cases` |
| Pilot jacket | `/products/custom-flag-name-with-badge-designed-pilot-jackets` |
| Mug | `/products/pilot-epaulette-1-2-3-4-lines-printed-customisable-mugs` |
