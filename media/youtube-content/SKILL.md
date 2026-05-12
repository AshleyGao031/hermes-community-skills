---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api
```

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## User Preferences
- **Be autonomous**: When the user shares a YouTube link, don't suggest "you can watch the video yourself" or "do you want me to extract the transcript?" — just extract it and deliver the result. If tools fail, switch strategies yourself. Never push work back to the user.
- **Save to study folder**: When extracting full content, also save a standalone file to `~/Documents/study/<descriptive-name>.md` and update `~/Documents/study/resources.md`. Don't ask — just do it.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
- **YouTube IP block** (RequestBlocked / IpBlock / LOGIN_REQUIRED): YouTube blocks requests from server/cloud IPs. Fall back to searching for the transcript on external sites:
  1. Get video title via `curl -s "https://noembed.com/embed?url=VIDEO_URL"`.
  2. Search DuckDuckGo: `curl -s "https://html.duckduckgo.com/html/?q=%22<TITLE>%22+transcript"` — look for every.to, podtail.com, ivoox.com, iheart.com links.
  3. For Every podcasts: try `https://every.to/podcast/transcript-<slugified-title>`.
  4. Fetch the transcript page HTML, extract the article body, strip HTML tags to get plain text.
  5. Also try YouTube Innertube API with ANDROID/IOS/WEB_CREATOR client contexts — though these may also be blocked.
- **Browser-based fallback**: if all API approaches fail, use the browser to navigate to the video page and extract the description/captions. YouTube may require login — if so, note the limitation and rely on web search results.
- **YouTube IP blocked** (`RequestBlocked` / `IPBlocked`): YouTube blocks transcript requests from datacenter/cloud IPs. Use the **Fallback: Creator transcript page** workflow below.
- **YouTube SSL/connection failure from China (GFW)**: `youtube-transcript-api` will throw `SSLError(SSLEOFError)` — YouTube is effectively unreachable. Browser access also requires login (bot detection). **Fallback to Chinese news articles**: Many speeches/videos get transcribed in full by Chinese media (36kr, 爱范儿, 量子位, 机器之心). Use browser to navigate to the Chinese article, extract the transcript section via `browser_console` DOM extraction (find the "附演讲原文" or similar marker, grab all `<p>` text after it). This is the most reliable path from China.

## Fallback: Creator Transcript Page

When `youtube-transcript-api` is blocked by YouTube (very common on server IPs), many podcasts and channels publish full transcripts on their own websites. Use this fallback sequence:

1. **Get video metadata** via noembed (works without auth):
   ```bash
   curl -s "https://noembed.com/embed?url=VIDEO_URL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('title'), d.get('author_name'))"
   ```
2. **Search DuckDuckGo** for a transcript page using the video title and channel name:
   ```bash
   curl -sL "https://html.duckduckgo.com/html/?q=%22VIDEO_TITLE%22+%22CHANNEL_NAME%22+transcript+OR+summary" -o /tmp/ddg.html
   ```
3. **Parse results** — look for links to the creator's own site (e.g., `every.to/podcast/transcript-*`, `podcast sites`, `blog posts with full transcript`). Extract URLs with regex on `class="result__a"` href attributes.
4. **Fetch the transcript page** with curl, strip HTML to get plain text. The transcript usually starts after a "Transcript" heading and timestamps like `(00:00:00)`.
5. **Clean up**: cut off footer content (ads, related posts, subscription prompts) by looking for markers like "Related Essays", "Share this post", "Thanks for rating".

### Known transcript URL patterns

| Channel/Site | Pattern |
|---|---|
| Every (AI & I podcast) | `https://every.to/podcast/transcript-<slug>` — slug is the episode title lowercased, hyphenated |
| General podcasts | Search `site:podcast.apple.com` or the podcast's own website |

### Tips
- The noembed endpoint also gives you `author_url` which often links to the podcast's website — check there first.
- DuckDuckGo HTML search is reliable without auth; avoid Google which blocks programmatic access.
- Transcript pages are usually large (40K-80K chars of text) — clean HTML aggressively before summarizing.
