# Используем официальный образ Python в качестве базового
FROM python:3.12-slim


# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем время хоста
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Gunicorn
RUN pip install gunicorn


# Копируем весь код приложения в рабочую директорию
COPY . .

