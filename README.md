# ServiceDesk API

## Описание проекта

ServiceDesk API — это система для управления обращениями пользователей, которая позволяет:
1. Пользователю отправлять сообщения на почту.
2. Автоматически создавать тикеты из писем пользователей.
3. Отправлять автоматические ответы пользователю, уведомляющие, что сообщение получено.
4. Предоставлять операторам интерфейс для работы с тикетами:
   - Назначение тикетов на оператора.
   - Обновление статуса тикета.
   - Закрытие тикета с уведомлением пользователя.
5. Поддерживать фильтрацию и сортировку тикетов через API.

### Основные функции
- Обработка писем, отправленных на указанный почтовый ящик (IMAP).
- Автоматическая отправка писем пользователям (SMTP).
- Работа с тикетами через REST API.
- Система уведомлений с использованием Celery.

---

## Стек технологий

- **Backend**: Python, FastAPI
- **Асинхронные операции**: SQLAlchemy (Async), IMAP (email), Celery
- **База данных**: PostgreSQL
- **Миграции**: Alembic
- **Очереди задач**: Celery + Redis
- **Тестирование**: pytest
- **Контейнеризация**: Docker, Docker Compose

---

## Как запустить проект

### Шаг 1: Клонирование репозитория
```bash
git clone <ссылка-на-репозиторий>
cd <название-папки-с-проектом>
```

### Шаг 2: Настройка окружения
Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные:

```env
# Настройки приложения
APP_TITLE=ServiceDesk API
DESCRIPTION=API для управления тикетами
VERSION=1.0.0

# Настройки базы данных
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# SMTP настройки
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_password
SENDER_NAME=name_gmail

# IMAP настройки
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
EMAIL_ACCOUNT=your_email@gmail.com
EMAIL_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Шаг 3: Установка зависимостей
Создайте виртуальное окружение и установите зависимости:
```bash
python3 -m venv venv
source venv/bin/activate  # Для macOS/Linux
venv\Scripts\activate     # Для Windows
pip install -r requirements.txt
```

### Шаг 4: Запуск проекта

#### Локальный запуск
Выполните команды:
```bash
# Запуск миграций базы данных
alembic upgrade head

# Запуск Redis (если он установлен локально)
redis-server

# Запуск Celery воркера
celery -A app.workers.celery_config.celery_app worker --loglevel=info

# Запуск приложения
uvicorn app.main:app --reload
```

#### Запуск с использованием Docker
Убедитесь, что установлен Docker и Docker Compose. Затем выполните:
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: `http://127.0.0.1:8000`.

---

## Эндпоинты API

Документация доступна по адресу: `http://127.0.0.1:8000/docs`.

Основные эндпоинты:
1. `GET /` - Проверка работы API.
2. `GET /tickets` - Получение списка тикетов с фильтрацией и сортировкой.
3. `POST /create_ticket` - Создание нового тикета.
4. `PATCH /assign/{ticket_id}/{operator_id}` - Назначение тикета оператору.
5. `PUT /tickets/{ticket_id}/close` - Закрытие тикета.
6. `POST /create_user` - Создание нового пользователя.
7. `POST /create_operator` - Создание нового оператора.

---

## Как запустить тесты

1. Убедитесь, что проект настроен (см. выше).
2. Запустите тесты с использованием `pytest`:
```bash
pytest tests/
```

3. Для вывода подробных результатов выполните:
```bash
pytest tests/ --verbose
```

---
