# Podcast Source Extraction Patterns

## 小宇宙FM (xiaoyuzhoufm.com)

**URL pattern:** `https://www.xiaoyuzhoufm.com/episode/{id}`

**Extraction steps:**
1. `browser_navigate` to the URL
2. Show notes are **collapsed by default** — must click the show notes section to expand
3. After expanding, extract via console:
   ```javascript
   document.querySelector('article')?.innerText
   ```
4. The article element contains: episode description, guest list, chapter markers with timestamps, key quotes, and host info

**Metadata available in page:**
- Duration (e.g., "77分钟")
- Play count (播放数)
- Comment count (评论数)
- Publication date
- Podcast name and host links

**Comments section:** Scroll down to see user comments with timestamps — useful for finding highlight moments.

**Video version:** Often available on Bilibili (哔哩哔哩) — check show notes for link.

**Text version:** Often on WeChat 公众号 — check show notes for link.

## YouTube

Use `youtube-content` skill with `scripts/fetch_transcript.py`. See that skill for fallback patterns when IP-blocked.

## WeChat 公众号

Use `markdown-proxy` skill with Jina reader (`r.jina.ai/URL`). Works for most public articles.

## Generic Article URLs

Try `markdown-proxy` first (cleaner output), fall back to `web_fetch` or `browser_navigate`.
