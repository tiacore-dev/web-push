from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from pywebpush import webpush, WebPushException

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()


# Функция отправки уведомления
def send_push_notification(subscription, message, private_key):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(
                {"title": "Scheduled Notification", "body": message}),
            vapid_private_key=private_key,
            vapid_claims={"sub": "mailto:your_email@example.com"}
        )
        print("Notification sent successfully!")
    except WebPushException as ex:
        print(f"Failed to send push: {str(ex)}")


@app.route('/schedule_notification', methods=['POST'])
def schedule_notification():
    data = request.json
    subscription = data.get('subscription')
    message = data.get('message', 'Default Notification Message')
    private_key = data.get('private_key')
    # Ожидается ISO-формат: 'YYYY-MM-DDTHH:MM:SS'
    notification_time = data.get('date')

    if not (subscription and message and private_key and notification_time):
        return jsonify({"error": "Missing required parameters"}), 400

    # Преобразование времени из строки в datetime
    # Если дата не указана, используем текущее время
    if not notification_time:
        notification_time = datetime.now()
        print(f"""Дата не указана. Используем текущее время: {
              notification_time}""")
    else:
        # Преобразование времени из строки в datetime
        try:
            notification_time = datetime.fromisoformat(notification_time)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}), 400

    # Планирование задачи
    scheduler.add_job(
        func=send_push_notification,
        trigger="date",
        run_date=notification_time,
        args=[subscription, message, private_key]
    )

    return jsonify({"message": "Notification scheduled successfully!"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5010)
