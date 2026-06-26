FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Отключение кэширования python-байтокода и буферизации логов
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Открываем порт бэка
EXPOSE 8000

# Запуск приложения
CMD ["python", "app.py"]