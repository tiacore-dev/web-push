import logging

# Настройка логгера


def setup_logger():
    logger = logging.getLogger('web_push')  # Используем именованный логгер
    logger.setLevel(logging.DEBUG)

    # Проверяем, был ли уже настроен логгер
    if not logger.handlers:
        # Добавляем обработчик для вывода логов в консоль
        console_handler = logging.StreamHandler()
        log_format = "%(asctime)s %(levelname)s: %(message)s"
        console_formatter = logging.Formatter(log_format)

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
