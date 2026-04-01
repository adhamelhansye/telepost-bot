import os
import logging
import feedparser
import requests
import json

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  CONFIGURE YOUR SOURCES HERE
# ─────────────────────────────────────────────

RSS_FEEDS = [
    # Web3 / blockchain security
    {"url": "https://rekt.news/feed/", "category": "DeFi exploit"},
    {"url": "https://blog.trailofbits.com/feed/", "category": "Web3 bug"},
    {"url": "https://blog.openzeppelin.com/feed.xml", "category": "Web3 bug"},
    # Cybersecurity news
    {"url": "https://feeds.feedburner.com/TheHackersNews", "category": "Cybersec news"},
    {"url": "https://www.bleepingcomputer.com/feed/", "category": "Cybersec news"},
    {"url": "https://portswigger.net/daily-swig/rss", "category": "CVE / Vuln"},
    # Writeups / CTF
    {"url": "https://medium.com/feed/tag/bug-bounty", "category": "Writeup"},
    {"url": "https://medium.com/feed/tag/web3-security", "category": "Writeup"},
    # Add more RSS feeds here
]

# Telegram public channels to scrape via t.me preview
# These are scraped without a bot — public channels only
TELEGRAM_CHANNELS = [
    "@web3security",
    "@CryptoSecNews",
    # Add your source channels here
]

# ─────────────────────────────────────────────


def fetch_rss_posts() -> list[dict]:
    posts = []
    for feed_cfg in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:5]:  # Latest 5 per feed
                post_id = entry.get("id") or entry.get("link", "")
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")

                # Strip HTML tags from summary
                import re
                summary = re.sub(r"<[^>]+>", "", summary).strip()
                summary = summary[:800]  # cap length

                content = f"{title}\n\n{summary}\n\n{link}".strip()
                if not content or len(content) < 80:
                    continue

                posts.append({
                    "id": f"rss:{post_id}",
                    "source": feed_cfg["url"],
                    "category": feed_cfg["category"],
                    "content": content,
                    "url": link,
                    "title": title,
                })
        except Exception as e:
            log.warning(f"Failed to parse feed {feed_cfg['url']}: {e}")

    return posts


def fetch_telegram_posts() -> list[dict]:
    """
    Scrapes public Telegram channel previews from t.me.
    For private channels or full history, use Telethon (requires phone auth).
    """
    posts = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TelePostBot/1.0)"}

    for channel in TELEGRAM_CHANNELS:
        slug = channel.lstrip("@")
        url = f"https://t.me/s/{slug}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                log.warning(f"t.me/{slug} returned {resp.status_code}")
                continue

            # Parse message text from HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            messages = soup.select(".tgme_widget_message_text")
            links = soup.select(".tgme_widget_message")

            for i, msg in enumerate(messages[:5]):
                text = msg.get_text(separator="\n").strip()
                if len(text) < 60:
                    continue

                # Try to get message link for dedup ID
                msg_wrap = links[i] if i < len(links) else None
                msg_url = ""
                if msg_wrap:
                    a = msg_wrap.select_one("a.tgme_widget_message_date")
                    msg_url = a["href"] if a else ""

                post_id = msg_url or f"tg:{slug}:{i}:{hash(text[:80])}"

                posts.append({
                    "id": f"tg:{post_id}",
                    "source": channel,
                    "category": "Cybersec news",  # default; override per channel if you want
                    "content": text[:1000],
                    "url": msg_url,
                    "title": text[:80],
                })

        except Exception as e:
            log.warning(f"Failed to fetch Telegram channel {channel}: {e}")

    return posts
