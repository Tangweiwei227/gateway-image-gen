---
name: gateway-image-gen
description: Generate or edit images by consuming the OpenAI-compatible images endpoint exposed by CLIproxyAPI (which proxies Codex CLI's image_generation tool to /v1/images/generations, default http://127.0.0.1:8317/v1). Use when the user wants an AI image / illustration / poster / icon / avatar / image edit through the local CLIproxyAPI proxy. Saves results locally and reports the path.
user-invocable: true
---

# Gateway Image Gen (gateway-image-gen)

Generate and edit images by consuming the OpenAI-compatible images endpoint
exposed by **CLIproxyAPI** ([router-for-me/CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)),
which proxies Codex CLI's image-generation capability to a local
`/v1/images/generations` endpoint. Text-to-image and image-editing (reference
image) are both supported. The bundled script uses only the Python 3 stdlib.

## When to use

- The user wants an AI-generated image: illustration, poster, icon, avatar,
  cover, concept art, product shot, etc., through the local CLIproxyAPI proxy.
- The user mentions CLIproxyAPI / CLI Proxy API / local proxy / 本地中转, or
  names an image model exposed by it (gpt-image-2.5, gpt-image-2.5-flare,
  gpt-image-2, gemini-3.1-flash-image, ...).
- The user provides a reference image and wants to edit / restyle / combine it.
- The user wants to reuse Codex's image capability (proxied by CLIproxyAPI)
  instead of paying per-image elsewhere.

**Do not use for:** ChatCut Desktop project images (use the ChatCut image tool),
Volcengine Ark Seedream (use `arkcli-gen`), Aliyun Bailian / Qwen / DashScope
(use `qwen-image-gen`), or MiniMax (use the MiniMax skill). This skill is for
the OpenAI-compatible images endpoint proxied by CLIproxyAPI (or any drop-in
OpenAI-compatible images endpoint).

## How it fits with CLIproxyAPI

[CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI) runs as a local
relay and can inject an `image_generation` tool for Codex CLI, exposing the
image models through the standard OpenAI-compatible route
`/v1/images/generations` (default listen address
`http://127.0.0.1:8317/v1`). This skill is the client for that endpoint: the
agent runs `scripts/gateway_image_gen.py`, which talks to the proxy the same
way any OpenAI-compatible images client would.

## Prerequisites

- CLIproxyAPI is running (default base URL
  `http://127.0.0.1:8317/v1`, override with `GATEWAY_BASE_URL` or `--base-url`).
- API key: set env `GATEWAY_API_KEY`, or pass `--api-key` (CLIproxyAPI can be
  configured to accept one via its generative-language-api-key parameter).
  Never hardcode keys in the script or documentation.

## Models

Run `--list-models` against your endpoint for the authoritative list. Verified
through CLIproxyAPI on gpt-image-2.5:

| Model | Notes |
|---|---|
| `gpt-image-2.5` | Default; text-to-image + image-edit verified |
| `gpt-image-2.5-flare` | Fast everyday generation |
| `gpt-image-2.5-sunburst` | Precision editing / complex creative work |
| `gpt-image-2` | Previous GPT image model |
| `gpt-image-1.5` | Earlier generation |
| `gemini-3.1-flash-image` | Gemini image model |

Honor an explicitly requested model; default to `gpt-image-2.5` otherwise.
An id not in the list can still be tried with `--model`.

## Supported parameters (verified against gpt-image-2.5)

| Param | Values | Default |
|---|---|---|
| size | `1024x1024` `1536x1024` `1024x1536` `2048x2048` | `1536x1024` |
| quality | `low` `medium` `high` `xhigh` `max` | `high` |
| background | `opaque` `transparent` (PNG cutout) | `opaque` |
| n | 1–4 (each saved separately) | 1 |
| edits | `--input <image path>` + prompt | — |

## Usage

```bash
# Text-to-image
python3 scripts/gateway_image_gen.py "a golden retriever running in a meadow at dusk, photorealistic" \
  --output-dir ./output

# Explicit model / size / quality / transparent background
python3 scripts/gateway_image_gen.py "minimal flat brand logo icon, transparent background" \
  --model gpt-image-2.5 --size 1024x1024 --quality high --background transparent

# Image edit from a reference
python3 scripts/gateway_image_gen.py "change this puppy into an orange cat" \
  --input ./dog.png --size 1024x1024

# Point at a different OpenAI-compatible endpoint
python3 scripts/gateway_image_gen.py "a cute robot" \
  --base-url https://your-relay.example.com/v1 --api-key "$GATEWAY_API_KEY"

# List models exposed by the endpoint
python3 scripts/gateway_image_gen.py --list-models
```

The script resolves the key → calls the endpoint → saves PNGs with timestamped
names into `--output-dir` (default `./output`) → prints the local paths.

## Workflow

1. Clarify: generate from text, or edit an existing image? Any reference image?
2. Write a specific prompt (subject + action + scene + style + lighting).
3. If the user provides a reference image path, use `--input` (edits endpoint).
4. Before generating, briefly state model / size / quality / count — especially
   for multiple images or high-cost settings.
5. Run the script, then report the saved paths; inspect the image if the
   current model supports image input.
6. To iterate, re-edit the latest result or regenerate.

## Rules

- Never hardcode or echo API keys: use `GATEWAY_API_KEY` / `--api-key`.
- Do not silently upgrade to `2048x2048` (slower and more expensive); only when
  the user asks, with a warning.
- Use `background: transparent` only when a cutout/overlay is needed (PNG).
- On connection failure / HTTP 503: check `GET <base-url>/models` and tell the
  user to confirm CLIproxyAPI is running — do not silently switch to another
  image skill.
- Report results as "saved to <path>" in the user's working directory.

## Checks

- Exit code 0 + printed local path → success.
- HTTP 4xx: check model id / params (e.g. unsupported size).
- HTTP 5xx / connection error: CLIproxyAPI down or upstream failure.

## License

MIT — see [LICENSE](./LICENSE).
