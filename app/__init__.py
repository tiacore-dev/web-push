import logging
from flask import Flask
from app.scheduler import scheduler
from app.routes import register_routes

# Настройка логирования
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Установите нужный уровень
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Добавьте обработчик к корневому логгеру
logging.getLogger().addHandler(console_handler)


def create_app():
    app = Flask(__name__)

    # Интеграция логов Flask и Gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    scheduler.start()
    register_routes(app)
    return app
