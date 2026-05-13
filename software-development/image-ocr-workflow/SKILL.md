---
name: image-ocr-workflow
description: "Extract text/data from images when vision_analyze fails: GLM API fallback, OCR pipeline, and structured output to Excel/PDF."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ocr, vision, image, excel, table-extraction, glm]
---

# Image OCR & Data Extraction Workflow

When `vision_analyze` fails (e.g. model not available on current plan), use this fallback chain to extract structured data from images.

## When to use

- User sends an image containing a table, receipt, or structured data
- `vision_analyze` returns an error (429, model not available, etc.)
- Need to convert image data to Excel, CSV, or structured JSON

## Fallback chain

### Step 1: Try vision_analyze

Always try first — it's the simplest path.

### Step 2: GLM API direct call

If vision_analyze fails, call the GLM vision API directly using credentials from `~/.hermes/.env`:

```python
import base64, json, urllib.request, os

with open(image_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Read API key from hermes .env
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("GLM_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break

# Try glm-4v-flash (free tier vision model)
url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
payload = {
    "model": "glm-4v-flash",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": "请完整识别图片中的所有数据内容，按行列结构列出。"}
        ]
    }]
}
req = urllib.request.Request(url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
)
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read().decode())
    text = result["choices"][0]["message"]["content"]
```

**Key points:**
- API base URL from hermes config: `~/.hermes/config.yaml` → `model.base_url`
- API key from: `~/.hermes/.env` → `GLM_API_KEY`
- Use `glm-4v-flash` for vision (free tier), not the text-only model
- Prompt in Chinese for best CJK recognition

### Step 3: Structured output to Excel

After extracting data, use openpyxl to create Excel:

```python
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Data"

# Write with formatting: bold headers, borders, number format
# Save to Desktop for easy access
wb.save(os.path.expanduser("~/Desktop/output.xlsx"))
```

**Pitfall**: On this Mac mini, `execute_code` runs in a sandbox without access to pip packages. Use `terminal` tool with heredoc (`python3 << 'EOF'`) instead for scripts needing openpyxl.

## Pitfalls

- **vision_analyze / browser_vision may fail with plan denial** (not just 429 rate limits). Error: `"Your current subscription plan does not yet include access to GLM-5V-Turbo"`. The built-in vision tools route to GLM-5V-Turbo which may not be on the current plan. The direct API call in Step 2 uses `glm-4v-flash` (different model) and may still work — try it.
- **If ALL vision fails**, tell the user honestly and ask them to describe or paste the image content. Don't burn turns retrying.
- **glm-4v-flash direct API call confirmed working as of 2026-05-11.** When vision_analyze fails with plan denial for GLM-5V-Turbo, the direct API call using `glm-4v-flash` (different model name) is the reliable fallback.
- **Chinese language prompts** give better CJK character recognition in OCR results.

## Session data recovery

If you need to reconstruct article content that was previously sent via `send_message` but not saved to disk:
1. Find the session JSON in `~/.hermes/sessions/session_YYYYMMDD_*.json`
2. Parse messages, looking for `tool_calls` entries where `function.name` = `send_message`
3. The article content is in `function.arguments` → `message` field (JSON string, parse it)
4. Join the parts in chronological order

## Environment notes

- Image cache: `/Users/ashley/.hermes/image_cache/`
- Documents path for saved files: `/Users/ashley/Documents/` (not Desktop)
- Windows compatibility: use English filenames for any files shared with colleagues
