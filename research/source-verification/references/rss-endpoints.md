# RSS Endpoint Discovery

## How to find RSS feeds for any company

### Common RSS URL patterns (try in order):
1. `/rss.xml`
2. `/feed`
3. `/blog/feed`
4. `/news/rss.xml`
5. `/feed.xml`
6. `/atom.xml`
7. `/blog/rss.xml`

### Discovery via HTML meta tags:
```bash
curl -sL 'https://example.com' | grep -i 'rss\|atom\|feed' | grep 'type="application'
```

### Discovery via common page links:
```bash
curl -sL 'https://example.com/blog' | grep -o 'href="[^"]*feed[^"]*"'
```

## Verified RSS Endpoints

### OpenAI
- **URL**: `https://openai.com/news/rss.xml`
- **Format**: RSS 2.0 with CDATA-wrapped titles and descriptions
- **Fields**: title, link, description, guid
- **Content**: All official blog posts and announcements
- **Example entry**:
  ```xml
  <item>
    <title><![CDATA[OpenAI and PwC collaborate to reimagine the office of the CFO]]></title>
    <description><![CDATA[OpenAI and PwC are partnering to help enterprises use AI agents...]]></description>
    <link>https://openai.com/index/openai-pwc-finance-collaboration</link>
    <guid isPermaLink="true">https://openai.com/index/openai-pwc-finance-collaboration</guid>
  </item>
  ```
- **Search pattern**: `grep -i 'keyword'`

### PwC
- **Global newsroom**: `https://www.pwc.com/gx/en/news-room/rss.xml` (may not exist)
- **US newsroom**: `https://www.pwc.com/us/en/about-us/newsroom.html` (no RSS found)
- **US press releases**: `https://www.pwc.com/us/en/about-us/newsroom/press-releases.html`
- **Alliance pages**: `https://www.pwc.com/us/en/technology/alliances/{partner-name}.html`
- **Tip**: PwC's global press release page (`/gx/en/news-room/press-releases.html`) exists but content is JS-rendered. Use Jina Reader to extract.

## Tips

- RSS feeds are served as static XML — no Cloudflare, no JS rendering, no CAPTCHAs
- They're the most reliable way to get exact URLs for official announcements
- Use `grep -i` for case-insensitive search across the feed
- RSS entries are chronological — newest first in most feeds
