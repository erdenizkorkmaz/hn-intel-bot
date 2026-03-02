# 🚀 Hacker News Intelligence Bot

Monitor Hacker News for relevant stories based on your keywords. Perfect for tracking startup trends, technology discussions, and industry insights.

## Features

- 🔍 **Keyword Monitoring**: Track multiple keywords across HN stories
- ⏰ **Time-based Filtering**: Only analyze recent stories (configurable)
- 📊 **Engagement Threshold**: Filter by minimum vote score
- 🔔 **Webhook Notifications**: Send alerts to Slack/Discord/your API
- 📈 **Automated Reports**: Markdown and JSON reports generated
- 🗂️ **Historical Data**: Reports archived in repository

## Setup

### 1. Configure Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | Example |
|--------|-------------|---------|
| `KEYWORDS` | Comma-separated keywords to track | `startup,SaaS,AI,machine learning` |
| `MIN_SCORE` | Minimum vote threshold | `10` |
| `MAX_AGE_HOURS` | How old stories can be | `24` |
| `WEBHOOK_URL` | (Optional) Notification endpoint | `https://hooks.slack.com/...` |

### 2. Run Manually

Go to **Actions → Hacker News Intelligence Bot → Run workflow**

### 3. Schedule

Runs automatically every 6 hours (configurable in `.github/workflows/automation.yml`)

## Output

- `report.md` - Human-readable markdown report
- `data.json` - Structured JSON data for further processing
- `reports/` - Historical reports committed to repo

## Example Report

```markdown
# 🚀 Hacker News Intelligence Report

**Generated:** 2026-03-02 14:30:00
**Keywords:** startup, SaaS, AI
**Matches Found:** 5

---

### 1. Show HN: My AI-powered startup idea validator

- **Score:** ⬆️ 245 | **Comments:** 💬 89
- **Author:** @founder123
- **Matched Keywords:** startup, AI
- **HN Link:** https://news.ycombinator.com/item?id=...
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export KEYWORDS="startup,SaaS,AI"
export MIN_SCORE="10"
export MAX_AGE_HOURS="24"

# Run locally
python bot.py
```

## License

MIT
