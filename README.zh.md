# gateway-image-gen

> 通过消费 **CLIProxyAPI** 代理出的 OpenAI 兼容 images 端点生成/编辑图片——CLIProxyAPI 把 Codex CLI 的图像生成能力暴露为标准 `/v1/images/generations` API。以「可复用 agent skill + 零依赖 Python CLI」的形式发布。

`gateway-image-gen` 是本机 [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) 代理的配套客户端：

- **Codex 图像能力，代理出来** —— CLIProxyAPI 为 Codex CLI 注入 `image_generation` 工具，把图像模型路由到标准 OpenAI 兼容的 `/v1/images/generations` 端点，默认监听 `http://127.0.0.1:8317/v1`。
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
- 正在运行的 [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI)，或任意其他 OpenAI 兼容 images 端点。默认 base URL 为 `http://127.0.0.1:8317/v1`（CLIProxyAPI 默认监听地址），可用 `GATEWAY_BASE_URL` 或 `--base-url` 覆盖。
- API Key：环境变量 `GATEWAY_API_KEY` 或 `--api-key`（CLIProxyAPI 通过 `generative-language-api-key` 参数接受 Key；端点不要求时可不填）。

## 与 CLIProxyAPI 的关系

[CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) 以本地中转形式运行，可为 Codex CLI 注入 `image_generation` 工具，把图像模型通过标准 OpenAI 兼容路由 `/v1/images/generations` 暴露出来（默认监听 `http://127.0.0.1:8317/v1`）。本 skill 就是这个端点的客户端：agent 执行 `scripts/gateway_image_gen.py`，与任何 OpenAI 兼容 images 客户端一样和代理对话。

## 安装与配置 CLIProxyAPI

CLIProxyAPI 是一个本地中转，把 Codex CLI（及其他 CLI）通过 OpenAI/Anthropic 兼容 API 代理出来。Codex 的 `image_generation` 工具注入后（[PR #2962](https://github.com/router-for-me/CLIProxyAPI/pull/2962)），图像模型就会出现：`GET /v1/models` 能列出它们，`/v1/images/generations` 与 `/v1/images/edits` 按标准 OpenAI 兼容 images API 工作。

1. **安装 CLIProxyAPI** —— 按官方快速开始安装你的系统版本（[英文](https://help.router-for.me/introduction/quick-start) / [中文](https://help.router-for.me/cn/introduction/quick-start)）；macOS 注意事项见 [issue #2064](https://github.com/router-for-me/CLIProxyAPI/issues/2064)。发布版在 [GitHub releases](https://github.com/router-for-me/CLIProxyAPI/releases)，Homebrew 公式由 [mxcl/pkg.so](https://github.com/mxcl/pkg.so/blob/main/combined/cliproxyapi.yml) 维护。
2. **配置** —— 把仓库根目录的 `config.example.yaml` 复制为 `config.yaml` 并编辑（v8 布局）：填 Codex 的上游凭证、监听地址（默认 `127.0.0.1:8317`）；如果希望代理要求 Key，在 `generative-language-api-key` 下列出可接受的 Key。
3. **启动** —— 运行代理，验证 images 端点（要带 Key；裸 `curl` 会返回 401
   鉴权失败，那只是「需要 Key」，不代表没在跑）：
   `curl -s -H "Authorization: Bearer $GATEWAY_API_KEY" http://127.0.0.1:8317/v1/models`。
4. **让 Codex 指向它**（如尚未配置）—— 在 Codex 配置里设 `base_url = "http://127.0.0.1:8317/v1"`，被代理的 `image_generation` 工具就会走 CLIProxyAPI。
5. **让本 skill 指向它** —— 这就是默认值，无需额外配置；若你的配置要求 Key，可 `export GATEWAY_API_KEY=...`。

> **macOS 提示** —— 版本相关安装/运行细节见 macOS 快速开始讨论串（[issue #2064](https://github.com/router-for-me/CLIProxyAPI/issues/2064)）。具体命令随版本而异，拿不准时以官方快速开始为准。

## 安装

### 最快：让 Agent 来做

把 **[Setup-agent-prompt.md](./Setup-agent-prompt.md)** 全文复制，丢给任意 AI Agent（Claude Code /
OpenClaw / DSH / Codex / Cursor）。Agent 会自动完成：安装 skill → 验证
CLIProxyAPI → 跑一张测试图 → 按使用规则开始生图。全程无需手工操作。

### 手动：作为 agent skill 安装

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
# 文生图（默认指向 CLIProxyAPI 的 http://127.0.0.1:8317/v1）
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

## 仓库布局 —— 谁读哪个文件

| 文件 | 读者 | 作用 |
|---|---|---|
| [Setup-agent-prompt.md](./Setup-agent-prompt.md) | 任意 AI Agent | **一键安装提示词**：复制丢给 agent，它自动安装 + 验证 + 开始使用 |
| [SKILL.md](./SKILL.md) | agent 运行时 | 安装后的 skill 本体：触发条件、参数、使用规则 |
| [README.md](./README.md) / [README.zh.md](./README.zh.md) | 人 | 概览、CLIProxyAPI 安装/配置手册、CLI 参考 |
| [scripts/gateway_image_gen.py](./scripts/gateway_image_gen.py) | agent / CLI | 真正调用端点的零依赖客户端 |

`Setup-agent-prompt.md` 和 `SKILL.md` **并不重复**——它们服务的时机不同：`Setup-agent-prompt.md`
是把 skill「安装进 agent」的引导提示词；`SKILL.md` 是安装之后 agent 使用的
本体（也是这个文件夹成为标准 agent skill 的关键）。`README.md` 是给人看的
手册，`Setup-agent-prompt.md` 只是把这个手册里的安装步骤变成了一段可复制的 agent 提示词。

## License

MIT —— 见 [LICENSE](./LICENSE)。
