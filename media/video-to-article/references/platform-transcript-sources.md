# 视频平台文稿获取备忘

## YouTube

- `youtube-transcript-api` 在 Mac mini 服务器 IP 上几乎 100% 被封
- noembed.com (`/embed?url=VIDEO_URL`) 可获取标题、作者、缩略图，不受封禁影响
- YouTube Innertube API (ANDROID/IOS/WEB_CREATOR clients) 同样被封锁
- 浏览器访问 YouTube 也可能要求登录

### 可靠的文稿来源

| 来源 | URL 模式 | 内容质量 | Mac mini 可用性 |
|------|----------|----------|----------------|
| every.to | `every.to/podcast/transcript-<slug>` | 完整 transcript，40K-80K 字符 | ✅ 可靠 |
| scripod.com | `scripod.com/episode/<id>` | highlights + chapters + transcript 摘要 | ✅ 可靠 |
| iheart.com | 搜索结果可找到 | 基本描述 | ✅ 可靠 |
| podtail.com | 搜索结果可找到 | 基本描述 | ✅ 可靠 |
| DuckDuckGo HTML search | `html.duckduckgo.com/html/?q=...` | 可靠，无需认证 | ⚠️ 偶尔触发 bot 检测 |

### 不可用的服务（Mac mini IP 被封）

以下服务在 Mac mini 上全部被封锁，不值得优先尝试：

| 服务 | 封锁方式 |
|------|----------|
| youtube-transcript-api | IP 封锁 |
| yt-dlp | "Sign in to confirm you're not a bot" |
| youtubetranscript.com | YouTube 端封锁，返回空 transcript |
| downsub.com | Cloudflare bot 验证 |
| Google Search | 验证码拦截 |
| Bing Search | 验证码拦截 |
| DuckDuckGo Lite | 偶尔触发 anomaly 检测 |
| YouTube 浏览器 transcript tab | 需要登录，panel 加载为空 |

### 搜索策略

```bash
curl -sL "https://html.duckduckgo.com/html/?q=%22<TITLE>%22+transcript" -H "User-Agent: Mozilla/5.0"
```

用正则提取：`class="result__a"` 的 href 和 `class="result__snippet"` 的内容。

### 文稿清洗

从 HTML 提取 transcript 后：
1. 找到 `(00:00:00)` 时间戳开始的 Transcript 部分
2. 截断于 "Related Essays"、"Share this post"、"Thanks for rating" 等页脚标记
3. 用正则清除 `<script>`, `<style>`, HTML tags
4. 替换 HTML entities: `&amp;` `&lt;` `&gt;` `&#39;` `&#x27;` `&#8216;` `&#8217;` `&quot;`

## 小宇宙 (xiaoyuzhoufm.com)

中文播客平台，show notes 信息密度极高。

### 页面结构

- 标题：`<h1>` 标签
- 时长/播放数/评论数：标题下方的静态文本
- Show notes 区域（`region "节目show notes"`）：
  - 📝 播客简介（完整内容摘要）
  - 👨⚕️ 嘉宾介绍
  - ⏱️ 时间戳（格式：`MM:SS 标题`）
  - 🌟 精彩内容（预提取的核心观点 + 原话引用）
- 评论区：听众评论常有有价值补充

### 采集方式

1. `browser_navigate` 打开页面
2. `browser_snapshot(full=true)` 获取完整内容
3. 可能需要点击"展开 Show Notes"按钮
4. 如果是克隆/翻译节目（如"跨国串门儿计划"克隆 Lenny's Podcast），额外搜索原始英文版本获取 transcript 补充细节

### 克隆节目识别

小宇宙上的"跨国串门儿计划"等节目是克隆自英文播客，用 AI 翻译+克隆人声制作：
- show notes 中会注明"翻译克隆自：XXX"
- 提供原始播客链接
- 可据此搜索原始 transcript 获取更完整内容
