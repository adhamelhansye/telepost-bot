import logging
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

def job():
    log.info("=== Scheduled run starting ===")
    try:
        run_pipeline()
    except Exception as e:
        log.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Africa/Cairo")  # UTC+2 — change to your timezone

    # 6:00 AM, 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM, 9:00 PM, 12:00 AM
    for hour in [6, 9, 12, 15, 18, 21, 0]:
        scheduler.add_job(
            job,
            CronTrigger(hour=hour, minute=0),
            id=f"post_{hour:02d}00",
            max_instances=1,
            coalesce=True,
        )

    log.info("Scheduler started. Posting at: 6AM 9AM 12PM 3PM 6PM 9PM 12AM (Cairo time)")
    scheduler.start()
