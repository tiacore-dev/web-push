from pywebpush import WebPushException
import logging
import json
import hashlib
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from pywebpush import webpush, WebPushException
from app.scheduler import scheduler

push_bp = Blueprint('push', __name__)

load_dotenv()

logger = logging.getLogger('web_push')

# Часовые пояса
novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
moscow_tz = pytz.timezone("Europe/Moscow")


URL = os.getenv('URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')


def send_push_notification(subscription, message):
    try:
        data = json.dumps(
            {
                "title": "Scheduled Notification",
                "body": message,
            },
            ensure_ascii=False
        )
        logger.info(f"Отправка данных: {data}")

        webpush(
            subscription_info=subscription,
            data=data,
            vapid_private_key=PRIVATE_KEY,
            vapid_claims={"sub": URL}
        )
        logger.info(f"Push успешно отправлен на {subscription['endpoint']}")
    except WebPushException as ex:
        logger.error(f"""Ошибка отправки пуша на {
                     subscription['endpoint']}: {str(ex)}""")
        if ex.response and ex.response.json():
            logger.error(f"Ответ сервера: {ex.response.json()}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке пуша: {str(e)}")


@push_bp.route('/schedule_notification', methods=['POST'])
def schedule_notification():
    """Эндпоинт для планирования push-уведомлений."""
    data = request.json
    logger.info(f"Received request data: {data}")

    subscription = data.get('subscription')
    message_data = data.get('data', {'text': 'Default Notification Message'})
    message = message_data.get('text')
    logger.info(f"Полученный текст сообщения: {message}")
    notification_time = data.get('date')

    if not (subscription and message):
        logger.warning("Missing required parameters")
        return jsonify({"error": "Missing required parameters"}), 400

    if not notification_time:
        logger.info("No notification time provided. Using current time.")
        notification_time = datetime.now()
    elif isinstance(notification_time, str):
        try:
            # Преобразование строки ISO 8601 в datetime
            notification_time = datetime.fromisoformat(notification_time)

            # Установка Новосибирского времени
            notification_time = novosibirsk_tz.localize(notification_time)
            logger.info(f"""Notification time in Novosibirsk timezone: {
                notification_time}""")

            # Конвертация в Московское время
            notification_time = notification_time.astimezone(moscow_tz)
            logger.info(f"""Converted notification time to Moscow timezone: {
                notification_time}""")
        except ValueError:
            logger.error(f"Invalid date format: {notification_time}")
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400
    else:
        logger.error(f"""Invalid type for notification_time: {
            type(notification_time)}""")
        return jsonify({"error": "Invalid notification_time format. Must be ISO string"}), 400

    # Проверка: отправить уведомление сразу, если время в прошлом
    current_time = datetime.now(moscow_tz)
    logging.info(f"Current Moscow time: {current_time}")

    if notification_time < current_time:
        logger.info(
            "Notification time is in the past. Sending push notification immediately.")
        try:
            send_push_notification(subscription, message)
            return jsonify({"message": "Notification sent immediately as the scheduled time was in the past."}), 200
        except Exception as e:
            logger.error(f"Failed to send immediate notification: {str(e)}")
            return jsonify({"error": "Failed to send immediate notification"}), 500

    # Планирование задачи
    try:

        # Генерация уникального ID через хеширование
        # Последние 10 символов
        short_endpoint = subscription['endpoint'][-10:]
        job_id = f"push-{short_endpoint}-{notification_time.isoformat()}"

        scheduler.add_job(
            func=send_push_notification,
            trigger="date",
            run_date=notification_time,
            args=[subscription, message],
            id=job_id,
            replace_existing=True,  # Обновляет существующую задачу с тем же ID
            misfire_grace_time=300,
        )
        logger.info(f"""Notification scheduled successfully for {
            notification_time}""")
    except Exception as e:
        logger.error(f"Failed to schedule notification: {str(e)}")
        return jsonify({"error": "Failed to schedule notification"}), 500

    return jsonify({"message": "Notification scheduled successfully!"}), 200
