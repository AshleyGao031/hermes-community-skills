---
name: source-verification
description: >
  Trace content claims back to primary sources. Find official blog posts,
  press releases, and announcements to verify facts. Triggers on:
  找信源, 核实, 查原文, fact check, source, 验证信息, 找链接
---

# Source Verification & Fact-Checking

When the user shares a claim (from her own content, news, or social media) and needs the original source links, follow this workflow.

## Core Workflow

### Step 1: Identify the claim and likely sources
- Extract key entities (company names, product names, people)
- Identify what type of source is needed (official blog, press release, news coverage, SEC filing)
- Note the claimed date — this is critical for narrowing search

### Step 2: RSS-first approach (highest success rate)
Company blogs and newsrooms almost always have RSS/Atom feeds. These bypass Cloudflare, CAPTCHA, and JavaScript rendering issues.

**Known RSS endpoints:**
- OpenAI: `https://openai.com/news/rss.xml`
- PwC Global: `https://www.pwc.com/gx/en/news-room/rss.xml` (may not exist)
- Generic pattern: Try `/rss.xml`, `/feed`, `/blog/feed`, `/news/rss.xml`

```bash
curl -sL 'https://openai.com/news/rss.xml' | grep -i 'keyword'
```

This is the **fastest** way to find exact blog post URLs. Use it FIRST, not last.

### Step 3: Direct URL construction (fast when it works)
Many sites use predictable URL patterns:
- OpenAI blog: `https://openai.com/index/{slug}`
- PwC press releases: `https://www.pwc.com/gx/en/news-room/press-releases/{year}/{slug}.html`
- PwC alliance pages: `https://www.pwc.com/us/en/technology/alliances/{partner}.html`

**Pitfall:** Direct URL guessing can waste many attempts. Use RSS first to get the exact URL.

### Step 4: Jina Reader for content extraction
Once you have the URL, use Jina Reader to bypass Cloudflare/JS rendering:

```bash
curl -sL 'https://r.jina.ai/{URL}' -H 'Accept: text/plain' | head -100
```

Works on: OpenAI, PwC, most news sites
Does NOT work on: Bloomberg (login wall), some paywalled sites

### Step 5: Search engines as last resort
Search engines (Google, Bing, DuckDuckGo) are heavily CAPTCHA'd when accessed programmatically. They should be the **last** resort, not the first.

**Pitfall:** Browser-based search (browser_navigate + browser_snapshot) hits CAPTCHAs from server environments. Don't spend more than 2 attempts on this.

## Site-Specific Knowledge

- **OpenAI blog**: RSS at `/news/rss.xml`, Jina works. Best entry point. RSS has title + URL + description
- **PwC**: RSS hard to find, Jina works. Alliance pages at `/us/en/technology/alliances/{name}.html`
- **PRNewswire**: No RSS, Jina fails (404s). Direct URLs unpredictable. Search RSS feeds of the SOURCE company instead
- **Bloomberg Tax**: No RSS, Jina fails (login wall). Paywalled. Skip unless the user has a subscription
- **Bloomberg News**: Same as above — paywall

## Output Format

When presenting sources to the user:

- Confirmed: Source name, URL, publication date, key info points
- Not found: Source name and reason

Always note date discrepancies between sources (e.g., OpenAI blog says May 4, but PRNewswire may say May 5).

For multi-claim fact-checking (videos, articles), see `references/video-fact-check-template.md`.

## Multi-Claim Fact-Checking (视频/文章核查)

When fact-checking a video or article with multiple claims, use this workflow:

1. **Extract all verifiable claims** — names, numbers, dates, technology claims, company status
2. **Batch search with DuckDuckGo HTML endpoint** (most reliable programmatic search):
   ```bash
   curl -s "https://html.duckduckgo.com/html/?q=QUERY" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" | python3 -c "
   import sys, re
   html = sys.stdin.read()
   text = re.sub(r'<[^>]+>', '|||', html)
   lines = [l.strip() for l in text.split('|||') if l.strip() and len(l.strip()) > 20]
   for line in lines[:40]: print(line)
   "
   ```
3. **Cross-reference numbers** — acquisition price, ARR, customer count often differ slightly across sources. Note the range.
4. **Check company current status** — acquired? shut down? pivoted? The video may be outdated.
5. **Present results as**: ✅ Confirmed / ⚠️ Partially accurate (with correction) / ❌ Wrong / 🔍 Unverifiable

**Pitfall:** Subagent delegation for web research is unreliable — subagents with `toolsets: ["web"]` often return empty summaries. Do the research yourself via terminal + curl when accuracy matters.

**Known reliable search endpoint:** DuckDuckGo HTML (`https://html.duckduckgo.com/html/?q=...`) — no CAPTCHA, no JS rendering needed, returns clean text snippets.

## Pitfalls

1. **Don't start with search engines** — RSS feeds are faster and more reliable
2. **Don't guess URLs** — 2-3 failed attempts is fine, but beyond that switch to RSS
3. **Note the actual publication date** — it may differ from the claimed date
4. **Bloomberg = paywall** — don't waste time trying to extract content
5. **PRNewswire URLs are unpredictable** — search the source company's RSS instead
6. **Don't trust subagent web research results** — subagents often fail to return useful data. For fact-critical searches, do it yourself via terminal + curl to DuckDuckGo HTML endpoint
7. **Company status changes** — a company described as "startup" in a video may have been acquired or shut down. Always verify current status.
