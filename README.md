# gateway-image-gen

> Generate and edit images by consuming the OpenAI-compatible images endpoint
> proxied by **CLIproxyAPI** — which exposes Codex CLI's image-generation
> capability as a standard `/v1/images/generations` API. Ships as a reusable
> agent skill plus a zero-dependency Python CLI.

`gateway-image-gen` is the client for the local [CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI)
proxy:

- **Codex image capability, proxied** — CLIproxyAPI injects an
  `image_generation` tool for Codex CLI and routes image models through the
  standard OpenAI-compatible `/v1/images/generations` endpoint, default listen
  address `http://127.0.0.1:8317/v1`.
- **Text-to-image** — `gpt-image-2.5` (and friends: `gpt-image-2.5-flare`,
  `gpt-image-2.5-sunburst`, `gpt-image-2`, `gemini-3.1-flash-image`, ...) via
  that endpoint.
- **Image editing** — restyle / modify a reference image through
  `/v1/images/edits` (multipart upload).
- **Zero dependencies** — the CLI uses only Python 3 stdlib (`urllib`).
- **Any OpenAI-compatible endpoint works** — point it elsewhere with
  `--base-url` / `GATEWAY_BASE_URL` and `--api-key` / `GATEWAY_API_KEY`.

## Features

- Verified against a gpt-image-2.5 endpoint: text-to-image and image-edit both
  return HTTP 200 and produce PNGs.
- Parametrized: `--model`, `--size` (1024² / 1536×1024 / 1024×1536 / 2048²),
  `--quality` (low → max), `--background` (opaque / transparent PNG cutout),
  `--n` (1–4).
- `--list-models` prints the image models your endpoint actually exposes.
- Timestamped local output; results are saved into `--output-dir`.

## Requirements

- Python 3 (stdlib only).
- [CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI) running, or any
  other OpenAI-compatible images endpoint. Default base URL:
  `http://127.0.0.1:8317/v1` (CLIproxyAPI's default listen address); override
  with `GATEWAY_BASE_URL` or `--base-url`.
- An API key via `GATEWAY_API_KEY` env var or `--api-key` (CLIproxyAPI accepts
  keys through its `generative-language-api-key` parameter; omit if your
  endpoint requires none).

## Install as an agent skill

Drop the folder into your agent's skills directory, e.g.:

```sh
# Claude Code / OpenClaw / DSH-style agent skills
mkdir -p ~/.agents/skills
cp -R gateway-image-gen ~/.agents/skills/
```

The skill's `SKILL.md` teaches the agent when to use it and how; the agent runs
`scripts/gateway_image_gen.py` for you. Or use the CLI directly:

## CLI usage

```sh
# Text-to-image (defaults to CLIproxyAPI at http://127.0.0.1:8317/v1)
python3 scripts/gateway_image_gen.py "a golden retriever running in a meadow at dusk, photorealistic" \
  --output-dir ./output

# Explicit model / size / quality / transparent background
python3 scripts/gateway_image_gen.py "minimal flat brand logo icon, transparent background" \
  --model gpt-image-2.5 --size 1024x1024 --quality high --background transparent

# Image edit from a reference
python3 scripts/gateway_image_gen.py "change this puppy into an orange cat" \
  --input ./dog.png --size 1024x1024

# Different endpoint
python3 scripts/gateway_image_gen.py "a cute robot" \
  --base-url https://your-relay.example.com/v1 --api-key "$GATEWAY_API_KEY"

# List models exposed by the endpoint
python3 scripts/gateway_image_gen.py --list-models
```

The script resolves the key → calls the endpoint → saves timestamped PNGs into
`--output-dir` (default `./output`) → prints the local paths.

## Model notes

Verified on a gpt-image-2.5 endpoint: `gpt-image-2.5` (default),
`gpt-image-2.5-flare`, `gpt-image-2.5-sunburst`, `gpt-image-2`,
`gpt-image-1.5`, `gemini-3.1-flash-image`. Run `--list-models` for the
authoritative list on your endpoint; an id outside the list can still be tried
with `--model`.

## Security

- Never hardcode or commit API keys. Use `GATEWAY_API_KEY` or `--api-key`.
- Generated content is saved locally; the script never sends local files
  anywhere except your configured endpoint.

## License

MIT — see [LICENSE](./LICENSE).
