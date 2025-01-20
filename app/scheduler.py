import logging
import os
from dotenv import load_dotenv
from apscheduler.events import EVENT_ALL, EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
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


def debug_jobs():
    jobs = scheduler.get_jobs()
    for job in jobs:
        logging.info(f"Job ID: {job.id}, Next run time: {job.next_run_time}")


scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults={
        "misfire_grace_time": 300,
    },
)

scheduler.add_job(
    debug_jobs,
    trigger=IntervalTrigger(seconds=30),  # Проверка каждые 30 секунд
)

# Установим интервал проверки задач
scheduler._jobstores["default"].max_interval = 5  # Проверять каждые 5 секунд


def event_listener(event):
    if event.code == EVENT_JOB_ADDED:
        logger.info(f"Job {event.job_id} was added.")
    elif event.code == EVENT_JOB_REMOVED:
        logger.info(f"Job {event.job_id} was removed.")
    elif event.code == EVENT_JOB_EXECUTED:
        logger.info(f"Job {event.job_id} executed successfully.")
    elif event.code == EVENT_JOB_ERROR:
        logger.error(f"Job {event.job_id} failed with exception: {
                     event.exception}")
    elif event.code == EVENT_JOB_MISSED:
        logger.warning(f"Job {event.job_id} was missed.")


scheduler.add_listener(event_listener, EVENT_ALL)

logger.info("Scheduler initialized with PostgreSQL-backed JobStore")
