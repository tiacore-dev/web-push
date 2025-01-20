import logging
import os
from dotenv import load_dotenv
# from pytz import timezone
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

# URL подключения к Postgres
DB_URL = os.getenv('DATABASE_URL')

# Настройка APScheduler с использованием SQLAlchemyJobStore
jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URL)
}

scheduler = BackgroundScheduler(
    # jobstores=jobstores, timezone=timezone("Europe/Moscow"))
    jobstores=jobstores)


def test_schedule():
    logging.info("Test job executed!")


def job_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} failed: {event.exception}")
    else:
        logging.info(f"Job {event.job_id} executed successfully.")


scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

logging.info("Scheduler initialized with PostgreSQL-backed JobStore")
