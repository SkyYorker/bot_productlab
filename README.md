# 🚀 Task Management System - Демо проект для PRODUCTLAB

Современная система управления задачами с Telegram-ботом, демонстрирующая навыки работы с FastAPI, PostgreSQL, Docker, RabbitMQ и CI/CD.

## 🎯 Особенности проекта

- ✅ **FastAPI** - современный асинхронный веб-фреймворк
- ✅ **PostgreSQL** - надежная база данных с миграциями
- ✅ **Docker & Docker Compose** - контейнеризация и оркестрация
- ✅ **Telegram Bot** - интеграция через aiogram
- ✅ **RabbitMQ** - асинхронная обработка задач
- ✅ **Rate Limiting** - защита от перегрузок
- ✅ **TDD/Тесты** - покрытие тестами (pytest)
- ✅ **GitLab CI/CD** - автоматический деплой
- ✅ **Alembic** - миграции базы данных
- ✅ **Pydantic** - валидация данных

## 📋 Технологический стек

- **Backend:** FastAPI, Python 3.11+
- **Database:** PostgreSQL 15
- **Message Queue:** RabbitMQ
- **Bot Framework:** aiogram 3.x
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Testing:** pytest, pytest-asyncio
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitLab CI

## 🏗️ Архитектура

```
┌─────────────┐
│ Telegram Bot│
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  FastAPI    │────▶│  PostgreSQL  │
│   Server    │     │   Database   │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│  RabbitMQ   │
│   Queue     │
└─────────────┘
```

## 🚀 Быстрый старт

### Требования

- Docker & Docker Compose
- Python 3.11+ (для локальной разработки)
- Git

### Запуск через Docker (рекомендуется)

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd productlab_demo

# Запустите все сервисы
docker-compose up -d

# Примените миграции
docker-compose exec api alembic upgrade head

# Проверьте статус
docker-compose ps
```

### Локальная разработка

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте .env файл
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Запустите PostgreSQL и RabbitMQ через Docker
docker-compose up -d postgres rabbitmq

# Примените миграции
alembic upgrade head

# Запустите API сервер
uvicorn app.main:app --reload

# В отдельном терминале запустите бота
python bot/main.py

# В отдельном терминале запустите воркер RabbitMQ
python workers/task_worker.py
```

## 📁 Структура проекта

```
productlab_demo/
├── app/                    # FastAPI приложение
│   ├── api/               # API роуты
│   ├── core/              # Конфигурация, безопасность
│   ├── models/            # SQLAlchemy модели
│   ├── schemas/           # Pydantic схемы
│   ├── services/          # Бизнес-логика
│   └── main.py            # Точка входа
├── bot/                    # Telegram бот
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   └── main.py            # Точка входа бота
├── workers/                # RabbitMQ воркеры
│   └── task_worker.py     # Обработчик задач
├── alembic/                # Миграции БД
│   └── versions/          # Файлы миграций
├── tests/                  # Тесты
│   ├── test_api/          # Тесты API
│   ├── test_bot/          # Тесты бота
│   └── conftest.py        # Конфигурация pytest
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile              # Docker образ для API
├── .gitlab-ci.yml          # GitLab CI/CD конфигурация
├── requirements.txt        # Python зависимости
└── README.md              # Документация
```

## 🔧 Основные функции

### API Endpoints

- `POST /api/tasks` - Создать задачу
- `GET /api/tasks` - Список задач (с пагинацией)
- `GET /api/tasks/{id}` - Получить задачу
- `PUT /api/tasks/{id}` - Обновить задачу
- `DELETE /api/tasks/{id}` - Удалить задачу
- `POST /api/tasks/{id}/complete` - Завершить задачу
- `GET /api/stats` - Статистика

### Telegram Bot Commands

- `/start` - Начать работу
- `/tasks` - Список задач
- `/add` - Добавить задачу
- `/start_task <ID>` - Начать работу над задачей (перевести в статус "в работе")
- `/complete <ID>` - Завершить задачу
- `/stats` - Статистика

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=app --cov=bot

# Только быстрые тесты
pytest -m "not slow"

# Конкретный тест
pytest tests/test_api/test_tasks.py::test_create_task
```

## 📊 CI/CD Pipeline

Проект включает GitLab CI/CD конфигурацию с этапами:

1. **Lint** - Проверка кода (flake8, black)
2. **Test** - Запуск тестов
3. **Build** - Сборка Docker образов
4. **Deploy** - Автоматический деплой

## 🔐 Безопасность

- Rate limiting на API endpoints
- JWT токены для аутентификации
- Валидация данных через Pydantic
- SQL injection защита через ORM
- CORS настройки

## 📈 Производительность

- Асинхронная обработка запросов
- Connection pooling для БД
- Кэширование через Redis (опционально)
- Очереди задач через RabbitMQ

## 🛠️ Разработка

### Создание миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
alembic upgrade head
```

### Добавление нового endpoint

1. Создайте схему в `app/schemas/`
2. Добавьте роут в `app/api/`
3. Реализуйте сервис в `app/services/`
4. Напишите тесты в `tests/`

## 📝 Лицензия

Демонстрационный проект для портфолио.

## 👤 Автор

Создано для демонстрации навыков работы с современным Python стеком.

