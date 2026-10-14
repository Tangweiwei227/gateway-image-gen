#!/usr/bin/env python3
"""
gateway_image_gen.py — Generate/edit images through any OpenAI-compatible
images API (gpt-image-2.5 series, etc.), e.g. a self-hosted gateway.

Usage:
  python3 gateway_image_gen.py "<prompt>" [--model gpt-image-2.5] [--size 1536x1024]
      [--quality high] [--background opaque] [--n 1] [--input <reference image>]
      [--base-url <url>] [--api-key <key>] [--output-dir ./output]
  python3 gateway_image_gen.py --list-models

Config:
  - API key:  --api-key <key> or env GATEWAY_API_KEY (required unless endpoint allows none)
  - Endpoint: --base-url <url> or env GATEWAY_BASE_URL (default http://127.0.0.1:8317/v1)

Dependencies: Python 3 stdlib only (urllib). No third-party packages.
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE = os.environ.get("GATEWAY_BASE_URL", "http://127.0.0.1:8317/v1")
DEFAULT_MODEL = "gpt-image-2.5"
SUPPORTED_SIZES = ("1024x1024", "1536x1024", "1024x1536", "2048x2048")


def http_json(base_url, api_key, path, payload, timeout=300):
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def http_multipart(base_url, api_key, fields, file_field, file_path, timeout=300):
    import uuid
    boundary = "----dsh" + uuid.uuid4().hex
    data = Path(file_path).read_bytes()
    ctype = "image/png" if str(file_path).lower().endswith(".png") else "image/jpeg"
    parts = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{Path(file_path).name}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n".encode("utf-8")
        + data
        + b"\r\n"
    )
    body = b"".join(parts) + f"--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def list_models(base_url, api_key):
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    models = [m["id"] for m in data.get("data", []) if "image" in m.get("id", "")]
    print("Available image models on this endpoint:")
    for m in sorted(models):
        print(f"  - {m}")
    return models


def save_images(out, output_dir: Path, tag: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    items = out.get("data", [])
    for i, item in enumerate(items):
        fname = f"{tag}_{int(time.time())}{'_' + str(i) if len(items) > 1 else ''}.png"
        dest = output_dir / fname
        if item.get("b64_json"):
            dest.write_bytes(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            urllib.request.urlretrieve(item["url"], str(dest))
        else:
            raise RuntimeError(f"Response item has neither b64_json nor url: {list(item.keys())}")
        saved.append(str(dest))
    return saved


def main():
    ap = argparse.ArgumentParser(description="Generate/edit images via an OpenAI-compatible images API")
    ap.add_argument("prompt", nargs="?", help="Generation prompt (ignored with --list-models)")
    ap.add_argument("--list-models", action="store_true", help="List image models exposed by the endpoint")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Model id (default {DEFAULT_MODEL})")
    ap.add_argument("--size", default="1536x1024", help="Size: " + " / ".join(SUPPORTED_SIZES))
    ap.add_argument("--quality", default="high", help="Quality: low / medium / high / xhigh / max")
    ap.add_argument("--background", default="opaque", help="Background: opaque / transparent")
    ap.add_argument("--n", type=int, default=1, help="Number of images, 1-4")
    ap.add_argument("--input", help="Reference image path (uses image-edits endpoint)")
    ap.add_argument("--base-url", default=DEFAULT_BASE, help="OpenAI-compatible base URL (default: $GATEWAY_BASE_URL or http://127.0.0.1:8317/v1)")
    ap.add_argument("--api-key", default=os.environ.get("GATEWAY_API_KEY", ""), help="API key (default: $GATEWAY_API_KEY)")
    ap.add_argument("--output-dir", default="output", help="Output directory (default ./output)")
    ap.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds")
    args = ap.parse_args()

    if args.list_models:
        list_models(args.base_url, args.api_key)
        return

    if not args.prompt:
        ap.error("Provide a prompt or use --list-models")

    if args.size not in SUPPORTED_SIZES:
        print(f"warning: size {args.size} not in supported set {SUPPORTED_SIZES} — sending anyway", file=sys.stderr)

    tag = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", args.prompt)[:40] or "image"
    try:
        if args.input:
            fields = {
                "model": args.model,
                "prompt": args.prompt,
                "size": args.size,
                "n": str(args.n),
            }
            out = http_multipart(args.base_url, args.api_key, fields, "image", args.input, timeout=args.timeout)
        else:
            payload = {
                "model": args.model,
                "prompt": args.prompt,
                "n": args.n,
                "size": args.size,
                "quality": args.quality,
                "background": args.background,
            }
            out = http_json(args.base_url, args.api_key, "/images/generations", payload, timeout=args.timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        print(f"Error: HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: cannot reach {args.base_url} (is the gateway running?): {e.reason}", file=sys.stderr)
        sys.exit(1)

    saved = save_images(out, Path(args.output_dir), tag)
    print(f"Saved {len(saved)} image(s):")
    for p in saved:
        print(f"  {p}")


if __name__ == "__main__":
    main()
