import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore

from sales_planning_requirement.jobs import (
    refresh_sales_planning_requirement_for_active_companies,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs the monthly Sales Planning vs Requirement refresh scheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        day = getattr(settings, "SALES_PLANNING_REQUIREMENT_REFRESH_DAY", 1)
        hour = getattr(settings, "SALES_PLANNING_REQUIREMENT_REFRESH_HOUR", 2)
        minute = getattr(settings, "SALES_PLANNING_REQUIREMENT_REFRESH_MINUTE", 30)

        scheduler.add_job(
            refresh_sales_planning_requirement_for_active_companies,
            trigger=CronTrigger(day=day, hour=hour, minute=minute),
            id="refresh_sales_planning_requirement_monthly",
            max_instances=1,
            replace_existing=True,
        )

        logger.info(
            "Sales planning requirement scheduler started: day=%s hour=%s minute=%s",
            day,
            hour,
            minute,
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Sales planning requirement scheduler running "
                f"(monthly day {day} at {hour:02d}:{minute:02d}). Press Ctrl+C to stop."
            )
        )

        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.WARNING("Scheduler stopped."))
