from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    name = "apps.scheduler"
    verbose_name = "Scheduler"

    def ready(self):
        import os
        # Only start in the main Django process, not during migrations or tests
        if os.environ.get("RUN_MAIN") == "true" or os.environ.get("DYNO"):
            self._start()

    def _start(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            from django.core.management import call_command
            import logging

            log = logging.getLogger(__name__)

            def job():
                log.info("Scheduler: running scrape_universities...")
                try:
                    call_command("scrape_universities")
                    log.info("Scheduler: done.")
                except Exception as e:
                    log.error(f"Scheduler error: {e}")

            scheduler = BackgroundScheduler(timezone="Asia/Tashkent")
            # Every Sunday at 03:00 AM Tashkent time
            scheduler.add_job(
                job,
                trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
                id="weekly_scrape",
                replace_existing=True,
            )
            scheduler.start()
            log.info("Scheduler started — scraper runs every Sunday at 03:00.")

        except ImportError:
            import logging
            logging.getLogger(__name__).warning(
                "apscheduler not installed — auto-scheduling disabled. "
                "Run manually: python manage.py scrape_universities"
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Scheduler failed to start: {e}")
