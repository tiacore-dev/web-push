import logging
import os
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from dotenv import load_dotenv
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

# URL подключения к Postgres
DB_URL = os.getenv('DATABASE_URL')

# Настройка JobStore с использованием Postgres
jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URL)
}

# Создание планировщика с хранилищем
scheduler = BackgroundScheduler(jobstores=jobstores)


# Настройка логирования APScheduler
scheduler._logger = logging.getLogger("apscheduler")
scheduler._logger.setLevel(logging.DEBUG)


def job_listener(event):
    if event.exception:
        logging.error(f"""Job {event.job_id} failed with exception: {
                      event.exception}""")
    else:
        logging.info(f"Job {event.job_id} executed successfully.")


scheduler.add_listener(job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

logging.info("Scheduler initialized with PostgreSQL-backed JobStore")
