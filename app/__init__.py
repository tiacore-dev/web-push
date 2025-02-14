import logging
from flask import Flask
from app.scheduler import scheduler
from app.routes import register_routes
from logger import setup_logger


def test_schedule():
    logging.info("Test job executed!")


def create_app():
    app = Flask(__name__)

    logger = setup_logger()

    # scheduler.start()
    logger.info("Scheduler started.")

    register_routes(app)
    logger.info("Routes registered")
    return app
