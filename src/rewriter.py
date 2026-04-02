import os
import logging
import requests

log = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "Web3Sec & CyberNews")
LANGUAGE = os.environ.get("POST_LANGUAGE", "English")
CUSTOM_INSTRUCTION = os.environ.get("CUSTOM_INSTRUCTION", "")

CATEGORY_PROMPTS = {
    "Web3 bug": "Focus on the technical vulnerability, what was exploited, and what developers should know.",
    "DeFi exploit": "Highlight the financial impact, the exploit mechanism, and what protocols should watch for.",
    "CVE / Vuln": "Mention the CVE ID if present, severity, affected software, and mitigation steps.",
    "Writeup": "Summarize the key technique or finding. Make it educational and engaging.",
    "Cybersec news": "Report the news clearly and concisely. Add context for why it matters.",
}


def rewrite_post(post: dict) -> str:
    category = post.get("category", "Cybersec news")
    category_hint = CATEGORY_PROMPTS.get(category, "")

    prompt = f"""You write posts for a Telegram channel called "{CHANNEL_NAME}" focused on Web3 security, cybersecurity bugs, exploits, CVEs, and writeups.

Your job: rewrite the source content as an engaging, human-written Telegram post.

Rules:
- Language: {LANGUAGE}
- Sound like a knowledgeable security researcher, not a bot or news aggregator
- Use plain text only — no markdown bold/italic
- Keep it under 900 characters so it fits cleanly in Telegram
- Add 3–5 relevant hashtags at the end (e.g. #web3security #exploit #CVE #bugbounty)
- If there's a source URL in the content, include it at the end as "Source: <url>"
- Category hint: {category_hint}
{f"Extra instruction: {CUSTOM_INSTRUCTION}" if CUSTOM_INSTRUCTION else ""}

Output ONLY the final post text. No preamble, no explanation.

Rewrite this for my Telegram channel:

{post['content']}"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 600,
            "temperature": 0.7,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        log.info(f"Rewrite done ({len(text)} chars)")
        return text
    except Exception as e:
        log.error(f"Gemini API error: {e} | Response: {resp.text if 'resp' in locals() else 'no response'}")
        raise
