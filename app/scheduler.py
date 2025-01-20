import logging
import os
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


logging.info("Scheduler initialized with PostgreSQL-backed JobStore")
