---
name: content-to-learning
description: "Turn external content (podcasts, videos, articles) into personalized learning materials. Extracts key concepts, translates to user's professional context, generates structured tutorials, and suggests content repurposing ideas. Triggers on: user shares a URL link (podcast/video/article), asks 'make a tutorial from this', 'what's important for me', 'summarize this for me', '学习笔记'."
---

# Content-to-Learning: Personalized Learning Material Generator

## When to Use

- User shares a URL (podcast, video, article, thread) and wants to learn from it
- User asks "有哪些信息对我来说非常重要" (what's important for me)
- User asks to create a tutorial or learning notes from external content
- User says "做个教程", "学习笔记", "帮我整理", "make a tutorial"
- User shares multiple links on the same topic (cross-reference)

## When NOT to Use

- User just wants raw transcript → use `youtube-content` or `markdown-proxy`
- User wants to save a link for later → use `Get笔记`
- User wants to publish the content as-is → use content publishing skills

## Core Workflow

### Step 1: Extract Content

Choose extraction method based on source:

| Source | Method |
|--------|--------|
| YouTube | `youtube-content` skill → `scripts/fetch_transcript.py` |
| YouTube (blocked) | **Jina Reader** → get description + linked blog posts → fetch blog via `web_fetch`. Often better quality than raw transcript. |
| 小宇宙FM podcast | Browser → expand show notes → `console: document.querySelector('article')?.innerText` |
| WeChat 公众号 | `markdown-proxy` skill (Jina reader) |
| General article | `markdown-proxy` or `web_fetch` |
| Twitter/X thread | `markdown-proxy` skill |

**Podcast-specific pitfall:** 小宇宙FM show notes are collapsed by default. Must click the show notes section to expand, then extract via console. The `article` element contains the full notes with timestamps and chapter markers.

### Step 2: Analyze for the User

Read the user's profile (USER.md / MEMORY.md) to understand:
- Their profession and role (e.g., Finance BP, Marketing, Engineering)
- Current projects and interests
- Technical skill level
- Content creation goals (e.g., 小红书)
- Learning style preferences

Then filter the content through their lens:

1. **Concept Translation** — Map technical jargon to their professional domain
   - Example: "Agent" → "有手有脑的AI同事"
   - Example: "Harness" → "你配置给Agent的所有规则和模板"
   - Example: "蒸馏" → "把隐性经验变成显性Skill"

2. **Relevance Scoring** — Rank each topic by:
   - Direct impact on their daily work (🔴 high)
   - Useful for their content creation (🟡 medium)
   - General knowledge (🟢 low)

3. **Actionable Mapping** — For each key concept, show:
   - What it means (in their language)
   - What they're already doing that relates
   - What they could do differently

### Step 3: Generate Tutorial

Use the template at `templates/tutorial-template.md`. Structure:

```
# 📻/🎬/📰 学习笔记：[Title]

> Source, duration, date, link

## 🎯 学习目标
What you'll understand after reading this

## 📖 核心概念解释（用[职业]语言翻译）
For each key concept:
- Original quote/idea
- Your professional translation
- What you're already doing
- What to do differently

## 🔥 金句收藏
Table of quotes + translations

## ✅ 行动清单
- 立即可做
- 持续关注
- 内容选题 ideas (if user creates content)

## 📚 延伸阅读
Related resources
```

### Step 4: Suggest Content Repurposing

If the user creates content (小红书, blog, etc.), suggest 2-3 angles:
- How to turn the learning into a post
- Which concepts would resonate with their audience
- What format works best (图文 vs 视频)

### Step 5: Deliver

Save to a project directory with English filename for messaging platform compatibility.

**⚠️ Pitfall: Telegram file sending with Chinese filenames**
Chinese characters in file paths cause "Media file not found" errors when sending via Telegram. Always copy to `/tmp/` with an English filename before sending:
```bash
cp "中文路径/文件.md" /tmp/english-filename.md
# Then send MEDIA:/tmp/english-filename.md
```

## Output Quality Standards

- **Not a raw summary** — every concept gets "translated" to user's context
- **Not generic advice** — every takeaway maps to something specific they can do
- **Not just extraction** — includes content repurposing ideas
- **Structured for scanning** — headers, tables, bullet points, emoji markers
- **Action-oriented** — ends with concrete next steps

## Cross-referencing Multiple Sources

When user shares multiple links on the same topic (e.g., podcast + YouTube video):
1. Extract each independently
2. Find overlapping concepts
3. Note where they agree/disagree
4. Create a unified tutorial that synthesizes both
5. Credit each source for its unique contributions

## References

- Tutorial template: `templates/tutorial-template.md`
- 
