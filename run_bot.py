"""
Скрипт для запуска бота из корневой папки
"""

import sys
from pathlib import Path

# Добавляем текущую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from bot.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

