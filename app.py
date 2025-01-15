from datetime import datetime
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from pywebpush import webpush, WebPushException

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def send_push_notification(subscription, message, private_key):
    """Отправка push-уведомления."""
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(
                {"title": "Scheduled Notification", "body": message}),
            vapid_private_key=private_key,
            vapid_claims={"sub": "mailto:your_email@example.com"}
        )
        logging.info(f"""Notification sent successfully to {
                     subscription['endpoint']}""")
    except WebPushException as ex:
        logging.error(f"""Failed to send push to {
                      subscription['endpoint']}: {str(ex)}""")


@app.route('/schedule_notification', methods=['POST'])
def schedule_notification():
    """Эндпоинт для планирования push-уведомлений."""
    data = request.json
    logging.info(f"Received request data: {data}")

    subscription = data.get('subscription')
    message = data.get('message', 'Default Notification Message')
    private_key = data.get('private_key')
    # Ожидается ISO-формат: 'YYYY-MM-DDTHH:MM:SS'
    notification_time = data.get('date')

    if not (subscription and message and private_key):
        logging.warning("Missing required parameters")
        return jsonify({"error": "Missing required parameters"}), 400

    # Если дата не указана, используем текущее время
    if not notification_time:
        notification_time = datetime.now()
        logging.info(f"""No notification time provided. Using current time: {
                     notification_time}""")
    else:
        try:
            notification_time = datetime.fromisoformat(notification_time)
            logging.info(f"""Notification time parsed successfully: {
                         notification_time}""")
        except ValueError:
            logging.error(f"Invalid date format: {notification_time}")
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400

    # Планирование задачи
    try:
        scheduler.add_job(
            func=send_push_notification,
            trigger="date",
            run_date=notification_time,
            args=[subscription, message, private_key]
        )
        logging.info(f"""Notification scheduled successfully for {
                     notification_time}""")
    except Exception as e:
        logging.error(f"Failed to schedule notification: {str(e)}")
        return jsonify({"error": "Failed to schedule notification"}), 500

    return jsonify({"message": "Notification scheduled successfully!"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5010)
