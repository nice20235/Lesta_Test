# Стадия сборки
FROM python:3.11-slim AS builder

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем зависимости отдельно для кеширования
COPY requirements.txt .

# Устанавливаем зависимости в виртуальное окружение
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Финальная стадия
FROM python:3.11-slim AS production

WORKDIR /app

# Копируем виртуальное окружение
COPY --from=builder /opt/venv /opt/venv

# Копируем проект
COPY --from=builder /app /app

# Добавляем venv в PATH
ENV PATH="/opt/venv/bin:$PATH"

# Настройки окружения
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings \
    PYTHONPATH="/app"

# Создаем директории для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Копируем entrypoint-скрипт
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]