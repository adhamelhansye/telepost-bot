# TelePost AI — 24/7 Telegram Channel Automation

Posts Web3 security bugs, CVEs, cybersec news, and writeups to your Telegram channel
automatically at fixed times daily. AI rewrites every post in a human voice.

## Schedule
Posts at: **6 AM · 9 AM · 12 PM · 3 PM · 6 PM · 9 PM · 12 AM** (Cairo / UTC+2)

---

## Quick Deploy — Railway (Free)

### 1. Create Telegram Bot
1. Open Telegram → search `@BotFather`
2. Send `/newbot` → follow prompts → copy the **token**
3. Add the bot as **admin** to your channel (can post messages)

### 2. Get your keys
- **Anthropic API key**: https://console.anthropic.com → API Keys
- **Channel ID**: your channel username (e.g. `@mychannel`) or numeric ID

### 3. Deploy to Railway
```bash
# Option A — GitHub (recommended)
# 1. Push this folder to a GitHub repo
# 2. Go to https://railway.app → New Project → Deploy from GitHub
# 3. Select your repo

# Option B — Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

### 4. Set Environment Variables on Railway
In your Railway project → Variables tab, add:

| Variable | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | your bot token |
| `TELEGRAM_CHANNEL_ID` | `@yourchannel` |
| `ANTHROPIC_API_KEY` | your Claude API key |
| `CHANNEL_NAME` | your channel display name |
| `POST_LANGUAGE` | `English` (or Arabic, Russian, etc.) |
| `CUSTOM_INSTRUCTION` | optional extra prompt instruction |

### 5. Add Persistent Volume (important!)
Railway free tier: Settings → Add Volume → mount at `/data`
This keeps the posted-IDs tracker alive across restarts.

---

## Configure Sources

Edit `src/sources.py`:

```python
RSS_FEEDS = [
    {"url": "https://rekt.news/feed/", "category": "DeFi exploit"},
    # Add any RSS feed URL here
]

TELEGRAM_CHANNELS = [
    "@web3security",
    # Add public Telegram channel usernames here
]
```

**Good RSS sources for Web3/Cybersec:**
- https://rekt.news/feed/
- https://feeds.feedburner.com/TheHackersNews
- https://www.bleepingcomputer.com/feed/
- https://blog.trailofbits.com/feed/
- https://portswigger.net/daily-swig/rss
- https://medium.com/feed/tag/web3-security

---

## Local Testing

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python -c "from src.pipeline import run_pipeline; run_pipeline()"
```

---

## How It Works

```
Every scheduled time:
  1. Fetch latest posts from RSS feeds + Telegram channels
  2. Filter out already-posted IDs (stored in /data/posted.json)
  3. Pick one fresh post randomly
  4. Send to Claude API → rewrite in your channel's voice
  5. Post to your Telegram channel via Bot API
  6. Save post ID so it never reposts the same content
```

---

## Free Tier Limits

| Service | Free limit |
|---|---|
| Railway | 500 hours/month (enough for 24/7) |
| Anthropic API | Pay-per-use (~$0.003 per post rewrite) |
| Telegram Bot API | Unlimited |

7 posts/day × 30 days = ~210 Claude API calls/month ≈ **< $1/month**
