"""APScheduler setup — integrates background jobs with FastAPI lifecycle."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import get_settings
from src.database.connection import get_async_session

scheduler = AsyncIOScheduler()


async def _run_job(job_func):
    """Wrapper to run a job with its own DB session."""
    async with get_async_session() as db:
        try:
            result = await job_func(db)
            await db.commit()
            settings = get_settings()
            if settings.debug:
                print(f"[scheduler] {job_func.__name__} → {result}")
        except Exception as e:
            await db.rollback()
            print(f"[scheduler] {job_func.__name__} ERROR: {e}")


async def _advance_days():
    from src.scheduler.jobs import advance_program_days
    await _run_job(advance_program_days)


async def _check_rollovers():
    from src.scheduler.jobs import check_season_rollovers
    await _run_job(check_season_rollovers)


async def _generate_reports():
    from src.scheduler.jobs import generate_weekly_reports
    await _run_job(generate_weekly_reports)


async def _check_streaks():
    from src.scheduler.jobs import check_streaks
    await _run_job(check_streaks)


def start_scheduler():
    """Register all jobs and start the scheduler."""
    settings = get_settings()
    if settings.app_env == "test":
        return

    scheduler.add_job(_advance_days, CronTrigger(hour=0, minute=5), id="advance_days")
    scheduler.add_job(_check_rollovers, CronTrigger(hour=0, minute=10), id="check_rollovers")
    scheduler.add_job(_check_streaks, CronTrigger(hour=0, minute=15), id="check_streaks")
    scheduler.add_job(_generate_reports, CronTrigger(day_of_week="sun", hour=6), id="weekly_reports")
    scheduler.start()


def stop_scheduler():
    """Shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
