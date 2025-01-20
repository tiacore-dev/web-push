import logging
import json
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from pywebpush import webpush, WebPushException
from app.scheduler import scheduler

push_bp = Blueprint('push', __name__)

load_dotenv()

# Часовые пояса
novosibirsk_tz = pytz.timezone("Asia/Novosibirsk")
moscow_tz = pytz.timezone("Europe/Moscow")

URL = os.getenv('URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')


def send_push_notification(subscription, message):
    """Отправка push-уведомления."""
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(
                {"title": "Scheduled Notification", "body": message}),
            vapid_private_key=PRIVATE_KEY,
            vapid_claims={"sub": URL}
        )
        logging.info(f"""Notification sent successfully to {
                     subscription['endpoint']}""")
    except WebPushException as ex:
        logging.error(f"""Failed to send push to {
                      subscription['endpoint']}: {str(ex)}""")


@push_bp.route('/schedule_notification', methods=['POST'])
def schedule_notification():
    """Эндпоинт для планирования push-уведомлений."""
    data = request.json
    logging.info(f"Received request data: {data}")

    subscription = data.get('subscription')
    message_data = data.get('data', {'text': 'Default Notification Message'})
    message = message_data.get('text')
    notification_time = data.get('date')

    if not (subscription and message):
        logging.warning("Missing required parameters")
        return jsonify({"error": "Missing required parameters"}), 400

    if not notification_time:
        logging.info("No notification time provided. Using current time.")
        notification_time = datetime.now()
    elif isinstance(notification_time, str):
        try:
            # Преобразование строки ISO 8601 в datetime
            notification_time = datetime.fromisoformat(notification_time)

            # Установка Новосибирского времени
            notification_time = novosibirsk_tz.localize(notification_time)
            logging.info(f"""Notification time in Novosibirsk timezone: {
                         notification_time}""")

            # Конвертация в Московское время
            notification_time = notification_time.astimezone(moscow_tz)
            logging.info(f"""Converted notification time to Moscow timezone: {
                         notification_time}""")
        except ValueError:
            logging.error(f"Invalid date format: {notification_time}")
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400
    else:
        logging.error(f"""Invalid type for notification_time: {
                      type(notification_time)}""")
        return jsonify({"error": "Invalid notification_time format. Must be ISO string"}), 400

    # Проверка: отправить уведомление сразу, если время в прошлом
    current_time = datetime.now(moscow_tz)
    if notification_time < current_time:
        logging.info(
            "Notification time is in the past. Sending push notification immediately.")
        try:
            send_push_notification(subscription, message)
            return jsonify({"message": "Notification sent immediately as the scheduled time was in the past."}), 200
        except Exception as e:
            logging.error(f"Failed to send immediate notification: {str(e)}")
            return jsonify({"error": "Failed to send immediate notification"}), 500

    # Планирование задачи
    try:
        scheduler.add_job(
            func=send_push_notification,
            trigger="date",
            run_date=notification_time,
            args=[subscription, message]
        )
        logging.info(f"""Notification scheduled successfully for {
                     notification_time}""")
    except Exception as e:
        logging.error(f"Failed to schedule notification: {str(e)}")
        return jsonify({"error": "Failed to schedule notification"}), 500

    return jsonify({"message": "Notification scheduled successfully!"}), 200
