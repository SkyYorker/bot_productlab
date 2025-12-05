#!/bin/bash
# Скрипт для запуска проекта

echo "🚀 Запуск Task Management System..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Запуск сервисов
echo "📦 Запуск Docker контейнеров..."
docker-compose up -d

# Ожидание готовности БД
echo "⏳ Ожидание готовности PostgreSQL..."
sleep 5

# Применение миграций
echo "🔄 Применение миграций..."
docker-compose exec api alembic upgrade head

echo "✅ Проект запущен!"
echo "📝 API доступен на http://localhost:8000"
echo "📚 Документация: http://localhost:8000/docs"
echo "🐰 RabbitMQ Management: http://localhost:15672"

