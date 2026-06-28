FROM hakaton_project-backend:latest

WORKDIR /app

# Создаем только папки, не файлы
RUN mkdir -p /app/static/uploads
RUN chmod -R 777 /app/static

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Убеждаемся, что папка для загрузок доступна для записи
RUN chmod -R 777 /app/static

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]