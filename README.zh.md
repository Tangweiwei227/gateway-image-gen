# gateway-image-gen

> 通过消费 **CLIproxyAPI** 代理出的 OpenAI 兼容 images 端点生成/编辑图片——CLIproxyAPI 把 Codex CLI 的图像生成能力暴露为标准 `/v1/images/generations` API。以「可复用 agent skill + 零依赖 Python CLI」的形式发布。

`gateway-image-gen` 是本机 [CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI) 代理的配套客户端：

- **Codex 图像能力，代理出来** —— CLIproxyAPI 为 Codex CLI 注入 `image_generation` 工具，把图像模型路由到标准 OpenAI 兼容的 `/v1/images/generations` 端点，默认监听 `http://127.0.0.1:8317/v1`。
- **文生图** —— 通过该端点调用 `gpt-image-2.5`（以及 `gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`、`gpt-image-2`、`gemini-3.1-flash-image` 等）。
- **图生图 / 编辑** —— 通过 `/v1/images/edits`（multipart 上传参考图）做改图、重绘。
- **零依赖** —— CLI 只依赖 Python 3 标准库（`urllib`）。
- **任意 OpenAI 兼容端点都可用** —— 用 `--base-url` / `GATEWAY_BASE_URL` 和 `--api-key` / `GATEWAY_API_KEY` 指向其他端点。

## 特性

- 已在 gpt-image-2.5 端点实测通过：文生图与图生图均返回 HTTP 200，产物为 PNG。
- 参数化：`--model`、`--size`（1024² / 1536×1024 / 1024×1536 / 2048²）、`--quality`（low → max）、`--background`（opaque / transparent 透明 PNG 抠图）、`--n`（1–4）。
- `--list-models` 列出你的端点实际暴露的图像模型。
- 本地输出带时间戳文件名，保存到 `--output-dir`。

## 前置要求

- Python 3（仅标准库）。
- 正在运行的 [CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI)，或任意其他 OpenAI 兼容 images 端点。默认 base URL 为 `http://127.0.0.1:8317/v1`（CLIproxyAPI 默认监听地址），可用 `GATEWAY_BASE_URL` 或 `--base-url` 覆盖。
- API Key：环境变量 `GATEWAY_API_KEY` 或 `--api-key`（CLIproxyAPI 通过 `generative-language-api-key` 参数接受 Key；端点不要求时可不填）。

## 与 CLIproxyAPI 的关系

[CLIproxyAPI](https://github.com/router-for-me/CLIProxyAPI) 以本地中转形式运行，可为 Codex CLI 注入 `image_generation` 工具，把图像模型通过标准 OpenAI 兼容路由 `/v1/images/generations` 暴露出来（默认监听 `http://127.0.0.1:8317/v1`）。本 skill 就是这个端点的客户端：agent 执行 `scripts/gateway_image_gen.py`，与任何 OpenAI 兼容 images 客户端一样和代理对话。

## 作为 agent skill 安装

把整个文件夹放进 agent 的 skills 目录，例如：

```sh
# Claude Code / OpenClaw / DSH 等 agent skills
mkdir -p ~/.agents/skills
cp -R gateway-image-gen ~/.agents/skills/
```

skill 里的 `SKILL.md` 会教 agent 何时使用、怎么用，agent 会替你执行
`scripts/gateway_image_gen.py`。也可以直接当 CLI 用：

## CLI 用法

```sh
# 文生图（默认指向 CLIproxyAPI 的 http://127.0.0.1:8317/v1）
python3 scripts/gateway_image_gen.py "黄昏草地奔跑的金毛犬，写实风" \
  --output-dir ./output

# 指定模型 / 尺寸 / 质量 / 透明背景
python3 scripts/gateway_image_gen.py "扁平风品牌 logo 图标，透明背景" \
  --model gpt-image-2.5 --size 1024x1024 --quality high --background transparent

# 图生图 / 编辑（基于参考图）
python3 scripts/gateway_image_gen.py "把这只小狗换成橘猫" \
  --input ./dog.png --size 1024x1024

# 换一个端点
python3 scripts/gateway_image_gen.py "一个可爱的机器人" \
  --base-url https://your-relay.example.com/v1 --api-key "$GATEWAY_API_KEY"

# 列出端点暴露的图像模型
python3 scripts/gateway_image_gen.py --list-models
```

脚本会自动完成：取 Key → 请求端点 → 保存带时间戳的 PNG 到 `--output-dir`（默认 `./output`）→ 打印本地路径。

## 模型说明

已在 gpt-image-2.5 端点验证：`gpt-image-2.5`（默认）、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`、`gpt-image-2`、`gpt-image-1.5`、`gemini-3.1-flash-image`。以你端点上的 `--list-models` 为准；清单外的模型 id 也可直接 `--model` 尝试。

## 安全

- 不要把 API Key 写死在脚本/代码里或提交进仓库。使用 `GATEWAY_API_KEY` 或 `--api-key`。
- 生成产物保存在本地；脚本只向你自己配置的端点发送数据。

## License

MIT —— 见 [LICENSE](./LICENSE)。
