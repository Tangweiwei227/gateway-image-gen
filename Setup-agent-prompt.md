# Setup-agent-prompt.md — 一键安装提示词（复制粘贴给任意 Agent 即可）

> 用法：把本文件全文复制给一个 AI Agent（Claude Code / OpenClaw / DSH /
> Codex / Cursor 等），它就会自动完成 gateway-image-gen 的安装、验证，并
> 从此刻起按下面的规则为你生图。无需手工操作。

---

你现在要帮我安装并启用 **gateway-image-gen**：一个通过本地
**CLIProxyAPI** 代理（把 Codex 的图像能力暴露成 OpenAI 兼容的
`/v1/images/generations` 接口）生成/编辑图片的 skill + CLI。请按以下步骤
完成安装、验证可用，并记住使用规则。

## 第 1 步 · 安装 skill

把仓库里的 `gateway-image-gen` 文件夹（含 `SKILL.md`、`scripts/`）复制到本
机的 agent skills 目录：

```sh
mkdir -p ~/.agents/skills
cp -R <本仓库的 gateway-image-gen 目录> ~/.agents/skills/
```

安装后应包含：`~/.agents/skills/gateway-image-gen/SKILL.md` 和
`~/.agents/skills/gateway-image-gen/scripts/gateway_image_gen.py`。

## 第 2 步 · 确认 CLIProxyAPI 可用

CLIProxyAPI 是本机中转，默认监听 `http://127.0.0.1:8317/v1`。请验证（带 Key，
否则会返回 401 鉴权失败——这并不代表服务没在跑）：

```sh
# 有 GATEWAY_API_KEY 环境变量时
curl -s -H "Authorization: Bearer $GATEWAY_API_KEY" http://127.0.0.1:8317/v1/models
```

- 有响应（列出 gpt-image-2.5 等图像模型）→ 继续。
- 连不上（连接被拒绝 / 超时）→ 提示用户先安装/启动 CLIProxyAPI（官方快速
  开始： https://help.router-for.me/introduction/quick-start ，macOS 注意
  https://github.com/router-for-me/CLIProxyAPI/issues/2064 ），装好后再继续。
- 返回 401 → 服务在跑，只是缺 Key：设置 `export GATEWAY_API_KEY=<用户提供的 Key>`
  后重试。

若本机环境需要 Key（CLIProxyAPI 配置了 `generative-language-api-key`），
设置环境变量：`export GATEWAY_API_KEY=<用户提供或已配置的 Key>`。

## 第 3 步 · 验证安装

```sh
python3 ~/.agents/skills/gateway-image-gen/scripts/gateway_image_gen.py --list-models
python3 ~/.agents/skills/gateway-image-gen/scripts/gateway_image_gen.py \
  "安装验证测试图：一只橘猫戴草帽" --size 1024x1024 --output-dir ~/Downloads
```

两张命令都成功、生成了 PNG → 安装完成。向用户确认：
「gateway-image-gen 已安装并验证可用，直接说‘帮我画…’即可。」

## 第 4 步 · 使用规则（从现在起一直遵守）

**何时用**：用户要任何 AI 图片/改图（插画、海报、图标、头像、封面、概念图、
产品图、重绘、合成），尤其是提到「本地中转 / CLIProxyAPI / 用代理生图」或
图像模型名（gpt-image-2.5、gpt-image-2.5-flare、gpt-image-2.5-sunburst、
gpt-image-2、gemini-3.1-flash-image 等）。不要用于 ChatCut 项目图、火山方舟
Seedream、百炼/Qwen、MiniMax（它们有各自的工具）。

**怎么调**：

```sh
# 文生图（默认指向 http://127.0.0.1:8317/v1）
python3 ~/.agents/skills/gateway-image-gen/scripts/gateway_image_gen.py "<prompt>" --output-dir <dir>

# 图生图 / 编辑（用户给了参考图路径时）
python3 ~/.agents/skills/gateway-image-gen/scripts/gateway_image_gen.py "<编辑描述>" --input <图片.png>

# 高级参数
--model gpt-image-2.5 --size 1024x1024 --quality high --background transparent --n 1
```

**行为规则**：
1. 生成前先说明模型/尺寸/质量/数量（多张或高成本参数时尤其要说）。
2. Prompt 写具体：主体 + 动作 + 场景 + 风格 + 光线；改图要精确描述
   （「把小狗换成橘猫」「改成夜景」「去掉背景」）。
3. 用户描述了图片但没给路径 → 先要路径再用 `--input`。
4. 生成后明确告知保存位置（「已保存到 <路径>」）；模型支持读图时先看一眼
   再声称成功。
5. 想改图 → 优先用 `--input` 编辑上一张结果，而非从头重生成。
6. 默认：模型 `gpt-image-2.5`、尺寸 `1536x1024`、质量 `high`、背景 `opaque`；
   只在用户要求时升 `2048x2048`（更慢更贵，需提示）。
7. 错误处理：HTTP 4xx → 检查模型名/参数（如尺寸不支持）；连不上或 5xx →
   CLIProxyAPI 没在跑，提示用户启动，不要悄悄换别的生图工具。

**安全**：绝不写死或回显 API Key（用 `GATEWAY_API_KEY` / `--api-key`）；
绝不把密钥提交进仓库。
