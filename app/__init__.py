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

    scheduler.start()
    logger.info("Scheduler started.")
    from datetime import datetime, timedelta
    from pytz import timezone
    test_time = datetime.now(timezone("Europe/Moscow")) + timedelta(seconds=10)
    scheduler.add_job(
        func=test_schedule,
        trigger="date",
        run_date=test_time
    )
    logging.info(f"Test job scheduled for {test_time}")

    register_routes(app)
    logger.info("Routes registered")
    return app
