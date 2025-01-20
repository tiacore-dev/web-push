import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pytz import timezone
# from pytz import timezone
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

# URL подключения к Postgres
DB_URL = os.getenv('DATABASE_URL')

logger = logging.getLogger('web_push')

# Настройка APScheduler с использованием SQLAlchemyJobStore
jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URL)
}

scheduler = BackgroundScheduler(
    jobstores=jobstores, timezone=timezone("Europe/Moscow"))
# jobstores=jobstores)


def test_schedule():
    logger.info("Test job executed!")


def add_test():        # Добавление тестовой задачи
    test_time = datetime.now(timezone("Europe/Moscow")) + timedelta(seconds=90)
    scheduler.add_job(
        func=test_schedule,
        trigger="date",
        run_date=test_time,
    )
    logger.info(f"Test job scheduled for {test_time}")


def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} executed successfully.")


scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

logger.info("Scheduler initialized with PostgreSQL-backed JobStore")
