# Simple Dockerfile

# FROM python:3.11-slim as build

# WORKDIR /app

# COPY . /app

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8000

# CMD ["uvicorn", "combined_asgi:app", "--host", "0.0.0.0", "--port", "8000"]



# # Вторая стадия: финальный образ
# FROM python:3.11-slim as production

# WORKDIR /app

# # Копируем только необходимые файлы из стадии build
# COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=build /app .

# # Открываем порт
# EXPOSE 8000

# # Запускаем приложение
# CMD ["uvicorn", "combined_asgi:app", "--host", "0.0.0.0", "--port", "8000"]



# Multi stage Dockerfile

# Стадия сборки
FROM python:3.11-slim as builder

WORKDIR /app

# Сначала копируем только requirements.txt для лучшего использования кеша
COPY requirements.txt .

# Устанавливаем зависимости в отдельную директорию
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Финальная стадия
FROM python:3.11-slim as production

WORKDIR /app

# Копируем установленные зависимости
COPY --from=builder /install /usr/local

# Копируем только нужные файлы приложения
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "combined_asgi:app", "--host", "0.0.0.0", "--port", "8000"]