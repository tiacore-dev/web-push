import os
import logging

from dotenv import load_dotenv
from app.scheduler import scheduler

load_dotenv()

port = os.getenv('FLASK_PORT')

bind = f"0.0.0.0:{port}"
workers = 4
timeout = 600

# Логи
loglevel = "debug"
errorlog = "-"  # Логи ошибок выводятся в stderr
accesslog = "-"  # Логи доступа выводятся в stdout
capture_output = True  # Перехватывать вывод stdout/stderr из приложения


# Добавляем флаг для предзагрузки приложения
preload_app = True


# Запуск `scheduler` только в мастере


def on_starting(server):
    logging.info("Starting Gunicorn, initializing scheduler...")
    scheduler.start()
    logging.info("Scheduler started.")


# Логирование событий после запуска воркеров


def post_fork(server, worker):
    logging.info(f"Worker {worker.pid} booted.")
