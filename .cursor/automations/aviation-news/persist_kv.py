#!/usr/bin/env python3
"""Persist a JPEG into gemini-image-worker IMAGES KV via Cloudflare API.

Use when POST /persist-bytes returns 401 (no worker Bearer in env) but
CLOUDFLARE_API_TOKEN can write KV. Verify GET 200 image/jpeg before using the URL.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
import uuid

ACC = "4c1f6c1c64b84870ac8f0f6766541c6f"
NS = "c9e746e2b819485fa95ff5b0a2e986e8"
ORIGIN = "https://gemini-image-worker.oevitan.workers.dev"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def persist_jpeg(data: bytes) -> str:
    if data[:3] != b"\xff\xd8\xff":
        raise SystemExit("not a JPEG (magic bytes)")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        raise SystemExit("CLOUDFLARE_API_TOKEN missing")
    key = str(uuid.uuid4()) + ".jpg"
    meta = json.dumps(
        {"contentType": "image/jpeg", "source": "persist-bytes", "persist": True, "expires_at": None}
    )
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{ACC}/storage/kv/namespaces/{NS}/values/{key}"
        f"?metadata={urllib.parse.quote(meta)}"
    )
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.loads(r.read().decode())
    if not body.get("success"):
        raise SystemExit(body)
    public = f"{ORIGIN}/img/{key}"
    req2 = urllib.request.Request(public, headers={"User-Agent": UA})
    with urllib.request.urlopen(req2, timeout=30) as r2:
        ct = r2.headers.get("content-type", "")
        blob = r2.read()
        if r2.status != 200 or "image/jpeg" not in ct.lower() or blob[:3] != b"\xff\xd8\xff":
            raise SystemExit(f"verify failed {public} {r2.status} {ct}")
    return public


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("jpeg_path")
    args = p.parse_args()
    data = open(args.jpeg_path, "rb").read()
    print(persist_jpeg(data))


if __name__ == "__main__":
    main()
