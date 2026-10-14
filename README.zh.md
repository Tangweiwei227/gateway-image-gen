# gateway-image-gen

> 通过任意 OpenAI 兼容的 images API 生成/编辑图片——自建本地中转、聚合网关或官方 `gpt-image-2.5` 端点均可。以「可复用 agent skill + 零依赖 Python CLI」的形式发布。

`gateway-image-gen` 是一个小巧、零依赖的图像生成 skill：

- **文生图** —— 通过标准 OpenAI 兼容的 `/v1/images/generations` 端点调用 `gpt-image-2.5`（以及 `gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`、`gpt-image-2`、`gemini-3.1-flash-image` 等）。
- **图生图 / 编辑** —— 通过 `/v1/images/edits`（multipart 上传参考图）做改图、重绘。
- **零依赖** —— CLI 只依赖 Python 3 标准库（`urllib`）。
- **自带网关** —— 通过 `--base-url` / `GATEWAY_BASE_URL` 和 `--api-key` / `GATEWAY_API_KEY` 指向任意 OpenAI 兼容的 images API；自建中转即可，无需按张付费的订阅。

## 特性

- 已在 `gpt-image-2.5` 网关实测通过：文生图与图生图均返回 HTTP 200，产物为 PNG。
- 参数化：`--model`、`--size`（1024² / 1536×1024 / 1024×1536 / 2048²）、`--quality`（low → max）、`--background`（opaque / transparent 透明 PNG 抠图）、`--n`（1–4）。
- `--list-models` 列出你的端点实际暴露的图像模型。
- 本地输出带时间戳文件名，保存到 `--output-dir`。

## 前置要求

- Python 3（仅标准库）。
- 一个可达的 OpenAI 兼容 images 端点。默认 base URL 为 `http://127.0.0.1:8317/v1`（本地中转示例），可用 `GATEWAY_BASE_URL` 或 `--base-url` 覆盖。
- API Key：环境变量 `GATEWAY_API_KEY` 或 `--api-key`（你的端点不要求时可不填）。

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
# 文生图
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

已在 gpt-image-2.5 网关验证：`gpt-image-2.5`（默认）、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`、`gpt-image-2`、`gpt-image-1.5`、`gemini-3.1-flash-image`。以你端点上的 `--list-models` 为准；清单外的模型 id 也可直接 `--model` 尝试。

## 安全

- 不要把 API Key 写死在脚本/代码里或提交进仓库。使用 `GATEWAY_API_KEY` 或 `--api-key`。
- 生成产物保存在本地；脚本只向你自己配置的端点发送数据。

## License

MIT —— 见 [LICENSE](./LICENSE)。
