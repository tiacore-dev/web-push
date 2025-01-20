import logging
from flask import Flask
from app.scheduler import scheduler
from app.routes import register_routes

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
    handlers=[
        logging.FileHandler("app.log", mode="a"),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)


def create_app():
    app = Flask(__name__)
    scheduler.start()
    register_routes(app)
    return app
