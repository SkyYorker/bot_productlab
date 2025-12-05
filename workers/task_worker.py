"""
RabbitMQ воркер для асинхронной обработки задач
"""

import asyncio
import json
import logging
from aio_pika import connect_robust, IncomingMessage
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_task(message: IncomingMessage):
    """Обработка задачи из очереди"""
    async with message.process():
        try:
            task_data = json.loads(message.body.decode())
            logger.info(f"Обработка задачи: {task_data}")
            
            # Здесь можно добавить логику обработки:
            # - Отправка уведомлений
            # - Обновление статусов
            # - Интеграция с внешними сервисами
            
            logger.info(f"Задача обработана: {task_data.get('id')}")
        except Exception as e:
            logger.error(f"Ошибка при обработке задачи: {e}")


async def main():
    """Главная функция воркера"""
    connection = await connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    
    # Объявление очереди
    queue = await channel.declare_queue("task_queue", durable=True)
    
    logger.info("🔄 Воркер запущен, ожидание задач...")
    
    # Подписка на очередь
    await queue.consume(process_task)
    
    try:
        await asyncio.Future()  # Бесконечное ожидание
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())

