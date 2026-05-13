# Jina Reader — Bypass Cloudflare & JS Rendering

## Usage
```bash
curl -sL 'https://r.jina.ai/{TARGET_URL}' -H 'Accept: text/plain'
```

## What it does
Jina Reader fetches a URL and returns clean Markdown content. It handles:
- Cloudflare challenges
- JavaScript rendering
- Cookie consent popups
- Most anti-bot measures

## Works well on
- OpenAI blog
- PwC website
- Most corporate blogs and newsrooms
- Wikipedia, GitHub, documentation sites

## Does NOT work on
- Bloomberg (any variant) — returns login page
- Some paywalled financial sites
- Sites requiring authentication
- Some sites with aggressive bot detection (returns 429)

## Output format
Returns Markdown with metadata:
```
Title: [page title]
URL Source: [original URL]
Warning: [any errors]
Markdown Content: [clean markdown]
```

## Tips
- Add `| head -N` to limit output for large pages
- Use `| grep -i 'keyword'` to search within content
- For full content: `| head -500` usually captures most articles
- The `Warning:` line tells you if the fetch had issues (404, 429, etc.)

## Pitfalls
1. **Don't use for search** — Jina Reader fetches specific URLs, it doesn't search
2. **Rate limits exist** — don't hammer it with rapid requests
3. **404s are common** — always check the Warning line for status codes
4. **Content may be truncated** — very long pages may not fully render
