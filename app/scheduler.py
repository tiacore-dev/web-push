import logging
import os
from dotenv import load_dotenv
from pytz import timezone
# from pytz import timezone
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
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
    # timezone=timezone("Europe/Moscow"),
    executors=executors,
    job_defaults={
        "misfire_grace_time": 300,
    },
)


def job_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} failed: {event.exception}")
    elif event.code == EVENT_JOB_MISSED:
        logging.warning(f"Job {event.job_id} was missed.")
    else:
        logging.info(f"""Job {event.job_id} executed successfully at {
                     event.scheduled_run_time}.""")


scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED |
                       EVENT_JOB_ERROR | EVENT_JOB_MISSED)

logger.info("Scheduler initialized with PostgreSQL-backed JobStore")
