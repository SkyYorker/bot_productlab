"""
Главный файл Telegram бота
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.handlers import task_handlers
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Регистрация обработчиков
dp.include_router(task_handlers.router)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для управления задачами.\n\n"
        "Доступные команды:\n"
        "/tasks - Список задач\n"
        "/add - Добавить задачу\n"
        "/start_task - Начать работу над задачей\n"
        "/complete - Завершить задачу\n"
        "/stats - Статистика"
    )


async def main():
    """Главная функция"""
    logger.info("🚀 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

