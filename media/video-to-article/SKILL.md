---
name: video-to-article
description: "将视频链接转换为深度文章。当用户发送 YouTube 等视频链接时调用，提取字幕后转换成阅读体验良好的深度长文。"
---

# Video to Article

## 触发条件

当用户发送视频链接（YouTube 等）并希望获取内容总结/文章时调用此 skill。

## 前置步骤：获取字幕

### YouTube 视频

1. 调用 `youtube-content` skill 获取视频字幕和元数据：
   ```bash
   python3 SKILL_DIR_MEDIA/scripts/fetch_transcript.py "URL" --text-only --timestamps
   ```
   `SKILL_DIR_MEDIA` = `/Users/ashley/.hermes/skills/media/youtube-content`

2. 如果字幕获取失败（YouTube 封 IP — 在 Mac mini 上几乎必然发生），按以下 Fallback 链依次尝试：

   **a. Get笔记（优先方案，成功率最高）**
   
   Get笔记服务端可正常访问 YouTube，保存链接后会自动抓取原文并生成 AI 总结和完整逐字稿。
   
   步骤：
   ```bash
   # 1. 保存链接到 Get笔记
   curl -s -X POST https://openapi.biji.com/open/api/v1/resource/note/save \
     -H "Authorization: $GETNOTE_API_KEY" \
     -H "X-Client-ID: $GETNOTE_CLIENT_ID" \
     -H "Content-Type: application/json" \
     -d '{"note_type":"link","link_url":"VIDEO_URL"}'
   ```
   返回 `data.tasks[0].task_id`（普通链接为异步任务）。
   
   ```bash
   # 2. 轮询任务进度（10-30秒间隔）
   curl -s -X POST https://openapi.biji.com/open/api/v1/resource/note/task/progress \
     -H "Authorization: $GETNOTE_API_KEY" \
     -H "X-Client-ID: $GETNOTE_CLIENT_ID" \
     -H "Content-Type: application/json" \
     -d '{"task_id":"TASK_ID"}'
   ```
   直到 `status` 为 `success` 或 `failed`。
   
   ```bash
   # 3. 获取笔记详情（含完整逐字稿和 AI 总结）
   curl -s "https://openapi.biji.com/open/api/v1/resource/note/detail?id=NOTE_ID" \
     -H "Authorization: $GETNOTE_API_KEY" \
     -H "X-Client-ID: $GETNOTE_CLIENT_ID"
   ```
   返回的 `data.note.web_page.content` 包含带时间戳的完整逐字稿，`data.note.content` 包含 AI 生成的结构化总结（含章节概要、金句、关键洞察）。
   
   ⚠️ 注意：
   - 需要 `GETNOTE_API_KEY` 和 `GETNOTE_CLIENT_ID` 环境变量（已配置在 .env）
   - 笔记 ID 是 int64，Python 原生支持无精度问题
   - 链接笔记返回的 `task_id` 在 `data.tasks[0].task_id`，不是 `data.task_id`
   - 拿到 task_id 后立即告知用户「正在处理」，后台轮询

   **b. noembed 元数据（获取标题等基础信息）**
   ```bash
   curl -s "https://noembed.com/embed?url=VIDEO_URL"
   ```

   **c. yt-dlp（偶尔可能成功）**
   ```bash
   python3 -m yt_dlp --write-auto-sub --sub-lang en --skip-download --sub-format json3 -o "/tmp/yt_sub" "VIDEO_URL"
   ```

   **d. 第三方 transcript 服务（大多被封锁）**
   - youtubetranscript.com、downsub.com、savesubs.com 等

   **e. 最终兜底：请用户提供 transcript 文件**

3. 如果能拿到视频元数据但拿不到字幕，告知用户并尝试 web search 找相关内容。

### 小宇宙（xiaoyuzhoufm.com）播客

1. 用浏览器打开播客页面，完整展开 show notes（可能需要点击"展开 Show Notes"按钮）
2. 小宇宙页面包含丰富的结构化内容：
   - **播客简介**（📝 本期播客简介）
   - **嘉宾介绍**（👨⚕️ 本期嘉宾）
   - **时间戳**（⏱️）— 每个章节标题和精确时间
   - **精彩内容**（🌟）— 预提取的核心观点和引用
   - **听众评论** — 常有有价值的补充观点
3. 同时搜索原始英文播客的 transcript（如果是翻译/克隆节目），用 DuckDuckGo 搜标题找 scripod.com 等来源的 highlights 补充细节
4. 小宇宙的 show notes + 原始播客的 transcript/高亮 结合使用，内容更完整

### 其他视频平台

- 对于非 YouTube 平台，先用浏览器访问页面提取可见内容
- 再通过 web search 搜索相关 transcript 或文稿
3. 如果能拿到视频元数据但拿不到字幕，告知用户并尝试 web search 找相关内容。

## 写作要求

### 读者定位

读者是一位充满好奇的年轻人，想通过视频学到有价值的知识和认知。

### 核心原则

- **重点突出**：舍弃片汤话和大道理，突出且不遗漏有价值的重点内容
- **深度理解**：充分展开每个重点，有上下文，有细节，有思考过程，不遗漏故事性论述
- **关注情感**：情感非常重要，传达作者的热情、困惑、兴奋等真实情感
- **超越视频**：充分发挥文字的优势，让读者的阅读体验超越观看视频
- **严格真实**：基于原始内容表达，不延展、不发挥

### 格式规范

- 少用破折号和不必要的引号、冒号等，少用排比句
- 中英文之间加入空格，数字和中文之间也加入空格
- 适当加入空行，让排版优雅大气
- 如果是中文内容，引号用全角中文引号：" 和 "
- 如果是英文内容，用英文引号

## 输出结构

严格按照以下结构输出：

```
## 视频信息

- 标题：xxx
- 作者：xxx
- 链接：xxx（YouTube 用 youtu.be 短链接）
- 时长：xxx
- 发布时间：xxx

## 视频简介

用一段引人入胜的文字，让读者瞬间能理解内容的独特价值，有欲望阅读。

## 详细内容

### [段落标题] `[起始时间 - 结束时间]`

正文内容...

### [段落标题] `[起始时间 - 结束时间]`

正文内容...
```

### 详细内容要求

- 按照内容的内在逻辑自然分段，每段用 `### 标题 [时间]` 格式
- 可长可短，充分展示文本写作能力
- 尽量保留原作者的语言风格和情感色彩
- 保留一些有价值的重要原话，用引号格式
- 有关键数据和案例时，做完整呈现

## 输出格式

用户可以选择以下输出格式（如果用户未指定，默认同时发 Discord + 保存 MD）：

1. **Discord 长文拆条**：每条消息不超过 ~1800 字，按段落自然拆分，避免在句子中间断开
2. **Markdown 文件**：保存到 `~/Documents/`，文件名用英文（如 `topic-keywords.md`），直接作为附件发送
3. **HTML 阅读页面**：当用户要求"阅读友好版"或"html格式"时生成。深色主题（#0f1117），左竖线章节标题，blockquote 高亮，表格卡片风格，最大宽度 780px，响应式。用 `delegate_task` 生成可大幅提高质量。保存到 `~/Documents/` 同名 `.html` 文件
4. **表格渲染成图片**：如果内容包含表格，用 HTML 渲染成深色卡片风格图片（深色渐变背景 `#1a1a2e` → `#2a2a4a`，圆角卡片，彩色难度标签），通过浏览器截图后作为附件发送。Discord 原生 markdown 表格渲染极丑，**永远不要**直接在 Discord 消息里发送 markdown 表格

## 表格转图片模板

当需要在 Discord 中展示表格数据时：

1. 创建 HTML 文件，使用深色卡片风格（参考 `templates/table-card.html`）
2. 用 `browser_navigate` 打开本地 HTML 文件
3. 截图保存后用 `MEDIA:` 附件发送
4. 同时发送一条简短说明文字

### 表格图片模板

当需要展示表格数据时，用浏览器加载一个 HTML 文件并截图发送：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 20px; background: #1a1a2e; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
  .table-card { background: linear-gradient(135deg, #1e1e3a 0%, #2a2a4a 100%); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); }
  .table-title { color: #e0e0ff; font-size: 18px; font-weight: 700; margin-bottom: 16px; }
  table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
  th { color: #8888aa; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 8px 16px; text-align: left; }
  td { background: rgba(255,255,255,0.04); padding: 14px 16px; color: #d0d0e8; font-size: 14px; }
  tr td:first-child { border-radius: 10px 0 0 10px; font-weight: 600; color: #a0a0ff; }
  tr td:last-child { border-radius: 0 10px 10px 0; }
</style>
</head>
<body>
<div class="table-card">
  <div class="table-title">表格标题</div>
  <table><!-- rows --></table>
</div>
</body>
</html>
```

步骤：write_file 保存到 /tmp/ → browser_navigate 打开 → 截图自动保存 → 用 MEDIA: 发送截图路径。

## 示例

用户发送：`https://youtu.be/x9BNBcP_C7Q`
→ 获取字幕 → 按上述结构和要求生成深度文章 → 发送到当前对话

用户发送：`https://www.xiaoyuzhoufm.com/episode/xxx`
→ 浏览器打开页面提取 show notes → 搜索原始英文 transcript 补充 → 生成深度文章

## 支持文件

- `references/platform-transcript-sources.md` — 各平台文稿获取策略和已知来源
- `templates/table-card.html` — Discord 表格图片渲染模板（深色卡片风格）
