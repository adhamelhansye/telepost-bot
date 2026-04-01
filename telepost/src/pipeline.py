import logging
import random
from src.sources import fetch_rss_posts, fetch_telegram_posts
from src.rewriter import rewrite_post
from src.poster import post_to_telegram
from src.tracker import was_posted, mark_posted

log = logging.getLogger(__name__)


def run_pipeline():
    """
    Full pipeline: fetch → filter seen → rewrite → post → mark done.
    Picks ONE best post per run to avoid spam.
    """
    all_posts = []

    # --- Collect from RSS ---
    try:
        rss_posts = fetch_rss_posts()
        log.info(f"RSS: fetched {len(rss_posts)} items")
        all_posts.extend(rss_posts)
    except Exception as e:
        log.warning(f"RSS fetch error: {e}")

    # --- Collect from Telegram ---
    try:
        tg_posts = fetch_telegram_posts()
        log.info(f"Telegram: fetched {len(tg_posts)} items")
        all_posts.extend(tg_posts)
    except Exception as e:
        log.warning(f"Telegram fetch error: {e}")

    if not all_posts:
        log.info("No new posts found this run.")
        return

    # --- Filter already-posted ---
    fresh = [p for p in all_posts if not was_posted(p["id"])]
    log.info(f"Fresh (not yet posted): {len(fresh)}")

    if not fresh:
        log.info("All fetched posts already posted. Skipping.")
        return

    # Pick one post per run (shuffle so we don't always take the first)
    chosen = random.choice(fresh)
    log.info(f"Chosen post: [{chosen['source']}] {chosen['id']}")

    # --- Rewrite with Claude ---
    try:
        rewritten = rewrite_post(chosen)
    except Exception as e:
        log.error(f"Rewrite failed: {e}")
        return

    if not rewritten:
        log.warning("Rewrite returned empty. Skipping.")
        return

    # --- Post to Telegram ---
    try:
        success = post_to_telegram(rewritten)
    except Exception as e:
        log.error(f"Posting failed: {e}")
        return

    if success:
        mark_posted(chosen["id"])
        log.info("Post sent and marked. Done.")
    else:
        log.error("Posting failed — not marking as posted.")
