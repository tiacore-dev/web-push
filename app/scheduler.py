import logging
import os
from dotenv import load_dotenv
from pytz import timezone
# from pytz import timezone
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.executors.pool import ThreadPoolExecutor
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


executors = {
    "default": ThreadPoolExecutor(10),
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    timezone=timezone("Europe/Moscow"),
    executors=executors,
    job_defaults={
        "misfire_grace_time": 300,
    },
)


def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} executed successfully.")


scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

logger.info("Scheduler initialized with PostgreSQL-backed JobStore")
