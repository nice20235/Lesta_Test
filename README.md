## 📁 Структура проекта

Lesta_Test/
├── core/                  # Настройки и логика Django
├── main/                  # Приложение с моделями/вьюшками
├── media/                 # Хранилище загружаемых файлов
├── static/, staticfiles/  # Статические файлы
├── templates/             # Шаблоны Django
├── combined_asgi.py       # Объединение Django и FastAPI в одном приложении
├── Dockerfile             # Docker-инструкция
├── docker-compose.yaml    # Docker Compose конфигурация
├── entrypoint.sh          # Скрипт запуска в контейнере
├── nginx.conf             # Конфигурация nginx (если используется)
├── requirements.txt       # Python-зависимости
├── .env                   # Переменные окружения
└── README.md              # Документация проекта


## 🚀 Запуск контейнера

```bash
# Сборка контейнера
docker build -t my-app .

# Запуск контейнера с .env переменными
docker run --env-file .env -p 8000:8000 lesta_app
```

🔗 Документация API (Swagger UI)
После запуска FastAPI доступен по адресу:
http://37.9.53.47/api/docs


## ⚙️ Конфигурируемые параметры (.env)

| Переменная               | Описание                                 | Значение по умолчанию |
| ------------------------ | ---------------------------------------- | --------------------- |
| APP_PORT                 | Порт запуска приложения                  | 8000                  |
| DJANGO_SETTINGS_MODULE   | Путь к настройкам Django                 | core.settings         |
| UPLOAD_DIR               | Путь к директории для загружаемых файлов | media/files           |
| MEDIA_ROOT               | Путь к директории медиафайлов            | media                 |
| STATIC_ROOT              | Путь к директории статических файлов     | staticfiles           |
| DEBUG                    | Режим отладки Django                     | True                  |
| SECRET_KEY               | Секретный ключ Django                     | your-secret-key       |


## 🧭 Версия приложения

`1.0.0`

## 📝 Changelog

### Версия 1.0.0
- Реализованы эндпоинты `/status`, `/metrics`, `/version`
- Реализована метрика:
  - Среднее время ответа (avg_response_time)
  - Кол-во запросов за последние 5 минут (request_count_last_5min)
- Добавлено сохранение метрик в SQLite
- Использование `.env` для параметров:
  - Порт сервера
  - Название БД
  - Путь к папке с файлами
- Добавлен `Dockerfile` и инструкция по запуску
