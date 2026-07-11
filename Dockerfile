# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости, необходимые для Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Playwright и браузеры
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем необходимые директории
RUN mkdir -p /app/data /app/my /app/.n8n-files

# Точка входа: запускаем основной скрипт с параметрами
ENTRYPOINT ["python", "auto_apply.py"]

# Аргументы по умолчанию: запуск в фоновом режиме (--schedule) с отправкой откликов (--apply)
CMD ["--schedule", "--apply", "--headless"]