# AGENTS.md — Agent Prompt for gateway-image-gen

This file is the operating prompt for AI agents (Claude Code, OpenClaw, DSH,
Codex, ...) that use this skill. Copy it into your agent's instructions, or
keep it in the repo — agents that read `AGENTS.md` will pick it up
automatically.

---

You have access to `gateway-image-gen`: a skill + CLI that generates and edits
images through the **CLIProxyAPI** local proxy (which exposes Codex CLI's image
capability as an OpenAI-compatible `/v1/images/generations` API).

## When to use it

Use this skill when the user asks for any AI-generated image or image edit:
illustrations, posters, icons, avatars, covers, concept art, product shots,
restyling, or compositing — **especially when they say "本地中转", "CLIProxyAPI",
"CLI Proxy API", "用代理生图", or name an image model** (gpt-image-2.5,
gpt-image-2.5-flare, gpt-image-2.5-sunburst, gpt-image-2,
gemini-3.1-flash-image, ...).

Do **not** use it for: ChatCut Desktop project images, Volcengine Ark Seedream,
Aliyun Bailian / Qwen / DashScope, or MiniMax — those have their own tools/skills.

## How to call it

```sh
# Text-to-image (defaults to CLIProxyAPI at http://127.0.0.1:8317/v1)
python3 scripts/gateway_image_gen.py "<prompt>" --output-dir <dir>

# Image edit from a reference image
python3 scripts/gateway_image_gen.py "<edit prompt>" --input <image.png>

# Advanced options
python3 scripts/gateway_image_gen.py "<prompt>" \
  --model gpt-image-2.5 --size 1024x1024 --quality high \
  --background transparent --n 1

# Discover which image models this endpoint exposes
python3 scripts/gateway_image_gen.py --list-models
```

## Behavior rules

1. **Ask first, then generate.** State model / size / quality / count before
   running, especially for multiple images or expensive settings.
2. **Write specific prompts.** Subject + action + scene + style + lighting.
   For edits, describe the change precisely ("change this puppy into an orange
   cat", "make it night time", "remove the background").
3. **Reference images:** if the user gives an image path, use `--input` (goes
   to the edits endpoint). Ask for the path if they describe an image instead.
4. **Report paths.** After generation, tell the user exactly where the PNG was
   saved ("已保存到 <path>"). Inspect the image if your model supports image
   input before claiming success.
5. **Iterate.** To change the result, edit the latest output with `--input`
   rather than regenerating from scratch, unless a fresh image is better.
6. **Defaults:** model `gpt-image-2.5`, size `1536x1024`, quality `high`,
   background `opaque`. Only upgrade to `2048x2048` when the user asks — it is
   slower and more expensive.
7. **Errors:**
   - HTTP 4xx → check model id / parameters (e.g. unsupported size).
   - Connection refused / HTTP 5xx → CLIProxyAPI is probably not running; tell
     the user to start it (default `http://127.0.0.1:8317/v1`). Do not silently
     switch to another image skill.

## Security

- Never hardcode or echo API keys. Use `GATEWAY_API_KEY` or `--api-key`.
- Never commit secrets to the repo.
