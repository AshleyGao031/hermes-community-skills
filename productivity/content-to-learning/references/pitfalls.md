# Pitfalls & Workarounds

## Telegram File Sending with Chinese Filenames

**Problem:** Files with Chinese characters in the path fail to send via Telegram. Error: "Media file not found, skipping".

**Root cause:** The MEDIA tag parser doesn't handle URL-encoded Chinese characters in file paths.

**Solution:** Always copy to `/tmp/` with an English filename before sending:
```bash
cp "projects/播客学习/2026-04-28-中文文件名.md" /tmp/podcast-tutorial-2026-04-28.md
# Then send: MEDIA:/tmp/podcast-tutorial-2026-04-28.md
```

**Rule:** When saving files that will be sent to Telegram, either:
1. Use English filenames from the start, OR
2. Copy to `/tmp/` with English name before sending

## Podcast Show Notes Collapse

**Problem:** 小宇宙FM and many podcast platforms collapse show notes by default. Browser snapshot returns minimal content.

**Solution:** Click the show notes section to expand, THEN use console to extract `document.querySelector('article')?.innerText`.

## YouTube Transcript Extraction (2026-05)

**Problem:** YouTube aggressively blocks transcript extraction from cloud IPs. All methods fail: `youtube-transcript-api`, `yt-dlp`, third-party services (youtubetranscript.com, Kome.ai full version).

**Best workaround — Blog post fallback:**
1. Use Jina Reader: `curl -s "https://r.jina.ai/YOUTUBE_URL"` — reliably returns video title, description, chapters, and linked blog posts
2. Look for the creator's own blog post (often linked in description). These are usually higher quality than raw transcripts — structured, edited, with screenshots
3. Use `web_fetch` on the blog post URL
4. Feed blog content into the content-to-learning workflow

**Why this is often BETTER than transcripts:**
- Blog posts are edited and structured (transcripts are raw speech-to-text)
- They often include screenshots, code samples, and formatted tables
- They contain the same content without filler words

**Verified example:** ChatPRD blog posts cover podcast episodes in full detail with images, making them superior to raw YouTube transcripts.

## Browser Session Expiry

**Problem:** Browser sessions can expire between tool calls. Navigating back to a page returns empty content.

**Solution:** If `browser_snapshot` returns empty after a previous successful read, re-navigate to the URL first.
