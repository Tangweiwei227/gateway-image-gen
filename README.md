# gateway-image-gen

> Generate and edit images by consuming the OpenAI-compatible images endpoint
> proxied by **CLIProxyAPI** — which exposes Codex CLI's image-generation
> capability as a standard `/v1/images/generations` API. Ships as a reusable
> agent skill plus a zero-dependency Python CLI.

`gateway-image-gen` is the client for the local [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)
proxy:

- **Codex image capability, proxied** — CLIProxyAPI injects an
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
- [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) running, or any
  other OpenAI-compatible images endpoint. Default base URL:
  `http://127.0.0.1:8317/v1` (CLIProxyAPI's default listen address); override
  with `GATEWAY_BASE_URL` or `--base-url`.
- An API key via `GATEWAY_API_KEY` env var or `--api-key` (CLIProxyAPI accepts
  keys through its `generative-language-api-key` parameter; omit if your
  endpoint requires none).

## Install & configure CLIProxyAPI

CLIProxyAPI is a local relay that proxies Codex CLI (and other CLIs) through an
OpenAI/Anthropic-compatible API. The image models appear once Codex's
`image_generation` tool is injected ([PR #2962](https://github.com/router-for-me/CLIProxyAPI/pull/2962));
then `GET /v1/models` lists them and `/v1/images/generations` + `/v1/images/edits`
work as any OpenAI-compatible images API.

1. **Install CLIProxyAPI** — follow the official quick start for your OS
   ([EN](https://help.router-for.me/introduction/quick-start) /
   [中文](https://help.router-for.me/cn/introduction/quick-start)); macOS notes
   are tracked in [issue #2064](https://github.com/router-for-me/CLIProxyAPI/issues/2064).
   Releases are published on the [GitHub repo](https://github.com/router-for-me/CLIProxyAPI/releases),
   and a Homebrew formula is maintained by [mxcl/pkg.so](https://github.com/mxcl/pkg.so/blob/main/combined/cliproxyapi.yml).
2. **Configure** — copy `config.example.yaml` from the repo root to
   `config.yaml` and edit (v8 layout): set your upstream credentials for Codex,
   the listen address (default `127.0.0.1:8317`), and, if you want the proxy to
   require a key, list accepted keys under `generative-language-api-key`.
3. **Run it** — start the proxy; verify the images endpoint:
   `curl http://127.0.0.1:8317/v1/models`.
4. **Point Codex at it** (if not already) — set
   `base_url = "http://127.0.0.1:8317/v1"` in your Codex config so the proxied
   `image_generation` tool routes through CLIProxyAPI.
5. **Point this skill at it** — that's the default; no extra setup needed.
   Optionally `export GATEWAY_API_KEY=...` if your config requires one.

> **macOS tip** — see the macOS quick-start thread
> ([issue #2064](https://github.com/router-for-me/CLIProxyAPI/issues/2064)) for
> version-specific install/run notes. Exact commands differ by release; when in
> doubt, prefer the official quick start above.

## Install as an agent skill

Drop the folder into your agent's skills directory, e.g.:

```sh
# Claude Code / OpenClaw / DSH-style agent skills
mkdir -p ~/.agents/skills
cp -R gateway-image-gen ~/.agents/skills/
```

The skill's `SKILL.md` teaches the agent when to use it and how; the agent runs
`scripts/gateway_image_gen.py` for you. Or use the CLI directly:

> **For agent setups:** a ready-to-paste agent prompt lives in
> [AGENTS.md](./AGENTS.md) — drop it into your agent's instructions (Claude
> Code / OpenClaw / DSH / Codex) or keep it in the repo where `AGENTS.md`
> readers pick it up automatically.

## CLI usage

```sh
# Text-to-image (defaults to CLIProxyAPI at http://127.0.0.1:8317/v1)
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
