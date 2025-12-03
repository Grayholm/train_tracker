# 🏋️ Train Tracker

Backend API для управления тренировками и упражнениями. Система позволяет пользователям создавать тренировки, добавлять упражнения, отслеживать прогресс и управлять своим фитнес-профилем.

## 📋 Содержание

- [Описание](#описание)
- [Основные возможности](#основные-возможности)
- [Технологический стек](#технологический-стек)
- [Архитектура](#архитектура)
- [Установка и настройка](#установка-и-настройка)
- [Конфигурация](#конфигурация)
- [Запуск проекта](#запуск-проекта)
- [API Endpoints](#api-endpoints)
- [Тестирование](#тестирование)
- [Docker](#docker)
- [Структура проекта](#структура-проекта)
- [Миграции БД](#миграции-бд)
- [Дополнительная документация](#дополнительная-документация)

## 📖 Описание

Train Tracker — это RESTful API на базе FastAPI, предназначенное для управления тренировками и упражнениями. Проект демонстрирует современные практики разработки backend-приложений: асинхронную архитектуру, многослойную структуру кода, тестирование и использование Docker для контейнеризации.

### Ключевые особенности архитектуры:

- **Асинхронный стек**: FastAPI + SQLAlchemy async + asyncpg для высокой производительности
- **Многослойная архитектура**: API → Services → Repositories → Models
- **Кастомные исключения**: Доменные исключения для чистой обработки ошибок
- **Транзакции**: Явное управление транзакциями с гарантией ACID
- **Фоновые задачи**: Celery + Redis для асинхронной отправки email
- **Кэширование**: Redis для кэширования часто запрашиваемых данных

## ✨ Основные возможности

### Аутентификация и авторизация
- Регистрация пользователей с подтверждением email
- JWT-токены для аутентификации
- Роли пользователей (Admin, User)
- Смена email и пароля

### Управление тренировками
- Создание, просмотр, обновление и удаление тренировок
- Добавление упражнений к тренировкам
- Частичное обновление тренировок (PATCH)
- Фильтрация тренировок по пользователю

### Управление упражнениями
- Просмотр всех доступных упражнений (с кэшированием)
- Добавление новых упражнений (только для администраторов)
- Обновление и удаление упражнений
- Категоризация упражнений

### Дополнительные функции
- Асинхронная отправка email через Celery
- Кэширование данных через Redis
- Автоматическая документация API (Swagger/OpenAPI)
- Миграции БД через Alembic

## 🛠 Технологический стек

### Backend Framework
- **FastAPI** 0.120.3 — асинхронный веб-фреймворк
- **Uvicorn** — ASGI сервер

### База данных
- **PostgreSQL** — реляционная БД
- **SQLAlchemy** 2.0.44 — async ORM
- **asyncpg** — асинхронный драйвер для PostgreSQL
- **Alembic** — миграции БД

### Аутентификация и безопасность
- **PyJWT** — JWT токены
- **Argon2** — хэширование паролей
- **passlib** — утилиты для работы с паролями

### Кэширование и очереди
- **Redis** 7.0.1 — кэширование и брокер сообщений
- **Celery** 5.5.3 — фоновые задачи
- **fastapi-cache2** — кэширование для FastAPI

### Валидация и конфигурация
- **Pydantic** 2.12.3 — валидация данных и схемы
- **pydantic-settings** — управление конфигурацией

### Тестирование
- **pytest** — фреймворк для тестирования
- **pytest-asyncio** — поддержка async тестов
- **pytest-mock** — мокирование
- **pytest-cov** — покрытие кода тестами
- **httpx** — HTTP клиент для тестов

### Инструменты разработки
- **Black** — форматирование кода
- **Ruff** — линтер
- **Pyright** — проверка типов

### Другие
- **Jinja2** — шаблоны для email
- **itsdangerous** — безопасные токены для email подтверждения

## 🏗 Архитектура

Проект следует принципам **Clean Architecture** с явным разделением слоёв:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)        │  ← HTTP запросы/ответы
│  (src/api/)                         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Services Layer                  │  ← Бизнес-логика
│  (src/services/)                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Repositories Layer                │  ← Доступ к БД
│  (src/repositories/)                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Models Layer (SQLAlchemy)      │  ← ORM модели
│  (src/models/)                      │
└─────────────────────────────────────┘
```

### Принципы архитектуры:

1. **Separation of Concerns**: Каждый слой отвечает за свою область
2. **Dependency Injection**: Зависимости передаются через параметры
3. **Repository Pattern**: Абстракция доступа к данным
4. **Service Pattern**: Бизнес-логика в сервисах
5. **Custom Exceptions**: Доменные исключения вместо низкоуровневых

## 🚀 Установка и настройка

### Требования

- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- Poetry (для управления зависимостями) или pip

### Установка зависимостей

#### С использованием Poetry:

```bash
poetry install
```

#### С использованием pip:

```bash
pip install -r requirements.txt
```

### Настройка базы данных

1. Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE training;
```

2. Настройте переменные окружения (см. раздел [Конфигурация](#конфигурация))

3. Примените миграции:

```bash
alembic upgrade head
```

## ⚙️ Конфигурация

Создайте файл `.env` в корне проекта со следующими переменными:

```env
# Режим работы (TEST, LOCAL, DEV, PROD)
MODE=LOCAL

# База данных PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_password
DB_NAME=training

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Secret key для подписи токенов
SECRET_KEY=your_secret_key_here

# Email настройки (для отправки писем подтверждения)
email_host=smtp.gmail.com
email_port=587
email_username=your_email@gmail.com
email_password=your_app_password

# Frontend URL (для ссылок в email)
frontend_url=http://localhost:3000

# Путь к шаблонам
templates_dir=templates
```

## 🏃 Запуск проекта

### Локальный запуск

1. Убедитесь, что PostgreSQL и Redis запущены

2. Запустите приложение:

```bash
# С Poetry
poetry run python src/main.py

# Или с pip
python src/main.py
```

3. Приложение будет доступно по адресу: `http://localhost:8000`

4. Документация API (Swagger): `http://localhost:8000/docs`
5. Альтернативная документация (ReDoc): `http://localhost:8000/redoc`

### Запуск Celery Worker

Для обработки фоновых задач (отправка email) необходимо запустить Celery worker:

```bash
celery --app=src.core.celery_config:celery_app worker -l INFO
```

### Запуск Celery Beat (опционально)

Для периодических задач:

```bash
celery --app=src.core.celery_config:celery_app beat -l INFO
```

## 📡 API Endpoints

### Аутентификация (`/auth`)

- `POST /auth/register` — Регистрация нового пользователя
- `POST /auth/login` — Вход в систему (получение JWT токена)
- `GET /auth/me` — Получить информацию о текущем пользователе
- `POST /auth/logout` — Выход из системы
- `PATCH /auth/edit_email` — Изменить email
- `PATCH /auth/edit_password` — Изменить пароль
- `GET /auth/register_confirm` — Подтверждение регистрации по токену

### Тренировки (`/workouts`)

- `GET /workouts` — Получить все тренировки текущего пользователя
- `GET /workouts/get/{workout_id}` — Получить конкретную тренировку
- `POST /workouts` — Создать новую тренировку
- `DELETE /workouts/delete/{workout_id}` — Удалить тренировку
- `PATCH /workouts/edit/{workout_id}` — Частично обновить тренировку
- `PATCH /workouts/{workout_id}` — Добавить упражнения к тренировке

### Упражнения (`/exercises`)

- `GET /exercises` — Получить все доступные упражнения (кэшируется)
- `GET /exercises/{exercise_id}` — Получить конкретное упражнение
- `POST /exercises` — Добавить новое упражнение (только для админов)
- `DELETE /exercises/{exercise_id}` — Удалить упражнение (только для админов)
- `PUT /exercises/{exercise_id}` — Полностью обновить упражнение (только для админов)
- `PATCH /exercises/{exercise_id}` — Частично обновить упражнение (только для админов)

**Примечание**: Все endpoints (кроме `/auth/register` и `/auth/login`) требуют аутентификации через JWT токен.

## 🧪 Тестирование

Проект включает unit-тесты и integration-тесты.

### Запуск всех тестов

```bash
pytest
```

### Запуск с покрытием кода

```bash
pytest --cov=src --cov-report=html
```

### Запуск только unit-тестов

```bash
pytest tests/unit_tests/
```

### Запуск только integration-тестов

```bash
pytest tests/integration_tests/
```

### Структура тестов

- `tests/unit_tests/` — Unit-тесты с мокированием зависимостей
- `tests/integration_tests/` — Интеграционные тесты с реальной БД
- `tests/conftest.py` — Общие фикстуры для тестов

## 🐳 Docker

### Создание Docker сети

```bash
docker network create myNetwork
```

### Запуск PostgreSQL

```bash
docker run --name training_db \
    -p 6432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=Qaz_wsx_123 \
    -e POSTGRES_DB=training \
    --network=myNetwork \
    -d postgres
```

### Запуск Redis

```bash
docker run --name training_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis
```

### Docker Compose

Для запуска всех сервисов (FastAPI, Celery Worker, Celery Beat) используйте docker-compose:

```bash
docker compose up --build
```

Подробнее о командах Docker см. [docs/docker.md](./docs/docker.md)

## 📁 Структура проекта

```
train_tracker/
├── src/
│   ├── api/              # API endpoints (FastAPI routers)
│   │   ├── auth.py       # Аутентификация
│   │   ├── exercises.py  # Упражнения
│   │   ├── workouts.py   # Тренировки
│   │   └── dependency.py # Зависимости (DB, User)
│   │
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   ├── db.py         # Настройка БД
│   │   ├── db_manager.py # Менеджер БД сессий
│   │   ├── redis_config.py # Настройка Redis
│   │   ├── redis_manager.py # Менеджер Redis
│   │   ├── celery_config.py # Конфигурация Celery
│   │   └── tasks.py      # Celery задачи
│   │
│   ├── models/           # SQLAlchemy ORM модели
│   │   ├── users.py
│   │   ├── workouts.py
│   │   ├── exercises.py
│   │   └── mixins/        # Миксины (ID, Timestamps)
│   │
│   ├── repositories/     # Слой доступа к данным
│   │   ├── base.py       # Базовый репозиторий
│   │   ├── users.py
│   │   ├── workouts.py
│   │   ├── exercises.py
│   │   └── mappers/       # Маппинг моделей → схемы
│   │
│   ├── services/         # Бизнес-логика
│   │   ├── base.py
│   │   ├── auth.py
│   │   ├── workouts.py
│   │   └── exercises.py
│   │
│   ├── schemas/          # Pydantic схемы
│   │   ├── users.py
│   │   ├── workouts.py
│   │   └── exercises.py
│   │
│   ├── migrations/       # Alembic миграции
│   │   └── versions/
│   │
│   ├── exceptions.py     # Кастомные исключения
│   └── main.py          # Точка входа приложения
│
├── tests/                # Тесты
│   ├── unit_tests/      # Unit-тесты
│   ├── integration_tests/ # Integration-тесты
│   └── conftest.py      # Фикстуры
│
├── templates/            # Шаблоны (email)
│   └── confirmation_email.html
│
├── docs/                 # Документация
│   └── docker.md
│
├── alembic.ini          # Конфигурация Alembic
├── docker-compose.yml   # Docker Compose конфигурация
├── Dockerfile           # Docker образ
├── pyproject.toml       # Poetry конфигурация
├── requirements.txt     # Зависимости (pip)
├── pytest.ini          # Конфигурация pytest
├── DESIGN.md           # Архитектурные решения
├── CHALLENGES.md       # Проблемы и решения
└── README.md           # Этот файл
```

## 🔄 Миграции БД

### Создание новой миграции

```bash
alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

### Просмотр истории миграций

```bash
alembic history
```

## 📚 Дополнительная документация

- [docs/docker.md](./docs/docker.md) — Команды для работы с Docker

## 👤 Автор

**Grayholm**  
Email: rodiongrayholm@gmail.com

## 📝 Лицензия

Этот проект создан в образовательных целях.

---

