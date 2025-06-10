# 📚 Lesta Test Application

Проект объединяет Django и FastAPI в одном приложении для работы с пользователями, документами и коллекциями. Поддерживается JWT-аутентификация, метрики и TF/IDF-анализ текстов.

## 📁 Структура проекта

├── core/ # Настройки Django
├── fastapi_app/ # Логика FastAPI
├── main/ # Django-приложение (модели, views)
├── media/ # Загружаемые файлы
├── static/ # Статические файлы
├── staticfiles/ # Собранные статич. файлы
├── templates/ # HTML-шаблоны
├── venv/ # Вирт. окружение (игнорируется)
│
├── .env # Переменные окружения
├── .gitignore # Исключения для git
├── baza.db # SQLite-база
│
├── combined_asgi.py # Объединение Django+FastAPI
├── manage.py # Django CLI
│
├── Dockerfile # Docker-инструкция
├── docker-compose.yaml # Конфигурация Docker
├── entrypoint.sh # Скрипт инициализации
├── nginx.conf # Конфиг nginx (опционально)
│
├── requirements.txt # Зависимости Python
└── README.md # Документация



## 🚀 Запуск проекта

### 🔧 Локальная установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера (режим разработки)
uvicorn combined_asgi:app --reload




🐳 Запуск в Docker
# Сборка контейнера
docker compose up.




🧭 Версия приложения
1.0.0




📝 Changelog
Версия 1.0.0

JWT-аутентификация

Управление документами (загрузка/чтение/удаление)

TF/IDF анализ для документов и коллекций

Управление коллекциями

Эндпоинты статуса и метрик

Конфигурация через .env

Поддержка Docker




🌐 Структура API эндпоинтов
Все API-эндпоинты используют префикс `/api/`.

Пример:  
`POST /api/users/register` вместо просто `POST /users/register`

📌 Примечание:  
- Swagger UI доступен по `/api/docs`




🔑 Авторизация
Метод	      Endpoint	     Описание

POST	/users/register ------------>	Регистрация

POST	/users/login ------------>	Вход

GET	    /users/logout ------------>	Выход

PATCH	/users/update ------------>	Изменение пароля

DELETE	/users/delete ------------>	Удаление аккаунта




📄 Документы
Метод 	      Endpoint	       Описание

GET	/documents/	 ------------> Список документов пользователя

POST /documents/upload	------------> Загрузка документа (.txt)

GET	/documents/{document_id} ------------>	Содержимое документа

GET	/documents/{document_id}/statistics ------------>	TF/IDF статистика

DELETE /documents/{document_id} ------------>	Удаление документа

GET /documents/{document_id}/huffman ------------>  Код Хаффмана




📁 Коллекции
Метод	        Endpoint	       Описание

GET	/collections/	------------>  Список коллекций

GET	/collections/{collection_id} ------------>  Документы в коллекции

GET	/collections/{collection_id}/statistics ------------> TF-IDF по коллекции

POST /collections/{collection_id}/{document_id} ------------>  Добавить документ в коллекцию

DELETE /collections/{cid}/{docid} ------------> Удалить документ из коллекции




📊 Метрики и статус
Метод	Endpoint	Описание

GET	/status ------------> 	Статус приложения

GET	/metrics ------------>	Метрики (время ответа, кол-во запросов)

GET	/version ------------>	Версия приложения





⚙️ Конфигурация окружения (.env)
Переменная	          Описание	        Пример значения

APP_PORT -	Порт запуска основного приложения	8000

DEBUG	 -  Включение отладочного режима (True / False)	True

DJANGO_SETTINGS_MODULE  - 	Путь к модулю настроек Django	core.settings

DJANGO_SECRET_KEY	 -  Секретный ключ Django	your-django-secret-key

JWT_SECRET_KEY  -  Секретный ключ для подписи JWT-токенов	super-secret

ALGORITHM  - 	Алгоритм шифрования JWT	HS256

ACCESS_TOKEN_EXPIRE_MINUTES  -	Время жизни JWT-токена (в минутах)	30

UPLOAD_DIR  - 	Директория для загружаемых файлов	media/files

MEDIA_ROOT  -  	Корневая папка для медиафайлов	media

STATIC_ROOT  - 	Каталог для статических файлов	staticfiles




