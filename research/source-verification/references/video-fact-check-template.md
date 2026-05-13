# Multi-Claim Fact-Checking Template

When the user asks you to fact-check a video, article, or social media post with multiple claims.

## Step 1: Extract Claims

List every verifiable claim:
- Person names + their stated background
- Company names + stated status
- Numbers (acquisition price, ARR, customer count, funding)
- Technology claims ("uses graph database", "AI-powered")
- Dates and timelines

## Step 2: Batch Search

Use DuckDuckGo HTML endpoint (most reliable programmatic search):

```bash
curl -s "https://html.duckduckgo.com/html/?q=QUERY" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" | \
  python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', '|||', html)
lines = [l.strip() for l in text.split('|||') if l.strip() and len(l.strip()) > 20]
for line in lines[:40]: print(line)
"
```

Search queries to try (in order):
1. `"{company name}" founder {claim}` — verify founder background
2. `"{company name}" funding ARR customers` — verify business metrics
3. `"{company name}" {technology claim}` — verify tech claims
4. `"{product name}" Intuit acquisition` — verify M&A claims

## Step 3: Cross-Reference

For each claim, note:
- Which sources confirm it
- Any discrepancies (e.g. $360M vs $397M acquisition price)
- Whether the info is current or outdated

## Step 4: Present Results

Format:
```
✅ **Claim** — Confirmed. Source: [name], [URL]
⚠️ **Claim** — Partially accurate. Actual: [correction]. Source: [name]
❌ **Claim** — Wrong. Reality: [fact]. Source: [name]
🔍 **Claim** — Unverifiable. No reliable sources found.
```

## Pitfalls

- **Subagent web research is unreliable** — do it yourself via terminal + curl
- **DuckDuckGo HTML > Google/Bing** — no CAPTCHA, no JS rendering needed
- **Company status changes fast** — a "startup" may have been acquired or shut down
- **Acquisition prices vary across sources** — note the range, pick the most authoritative
- **Wikipedia may not have articles for newer companies** — don't rely on it as sole source
