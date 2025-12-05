"""
Обработчики команд для задач
"""

import sys
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp
from app.core.config import settings

router = Router()
API_URL = f"http://localhost:8000/api"  # В продакшене используйте переменную окружения


class TaskCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Показать список задач"""
    telegram_id = message.from_user.id
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/tasks", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                tasks = data.get("items", [])
                
                if not tasks:
                    await message.answer("📝 У вас пока нет задач")
                    return
                
                text = "📋 Ваши задачи:\n\n"
                for task in tasks[:10]:  # Показываем первые 10
                    status_emoji = {
                        "pending": "⏳",
                        "in_progress": "🔄",
                        "completed": "✅",
                        "cancelled": "❌"
                    }
                    priority_emoji = {
                        "low": "🟢",
                        "medium": "🟡",
                        "high": "🔴",
                        "urgent": "🔴"
                    }
                    
                    emoji = status_emoji.get(task["status"], "📝")
                    priority = priority_emoji.get(task["priority"], "🟡")
                    
                    text += f"{emoji} {task['title']} {priority}\n"
                    if task.get("description"):
                        text += f"   {task['description'][:50]}...\n"
                    text += "\n"
                
                await message.answer(text)
            else:
                await message.answer("❌ Ошибка при получении задач")


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """Начать создание задачи"""
    await message.answer("📝 Введите название задачи:")
    await state.set_state(TaskCreation.waiting_for_title)


@router.message(TaskCreation.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    """Обработать название задачи"""
    await state.update_data(title=message.text)
    await message.answer("📄 Введите описание задачи (или /skip чтобы пропустить):")
    await state.set_state(TaskCreation.waiting_for_description)


@router.message(Command("skip"), TaskCreation.waiting_for_description)
async def skip_description(message: Message, state: FSMContext):
    """Пропустить описание"""
    await create_task(message, state)


@router.message(TaskCreation.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Обработать описание задачи"""
    await state.update_data(description=message.text)
    await create_task(message, state)


async def create_task(message: Message, state: FSMContext):
    """Создать задачу через API"""
    data = await state.get_data()
    user = message.from_user
    
    task_data = {
        "title": data["title"],
        "description": data.get("description"),
        "priority": "medium"
    }
    
    params = {
        "telegram_id": user.id,
    }
    if user.username:
        params["username"] = user.username
    if user.first_name:
        params["first_name"] = user.first_name
    if user.last_name:
        params["last_name"] = user.last_name
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/tasks",
                json=task_data,
                params=params
            ) as resp:
                if resp.status == 201:
                    await message.answer("✅ Задача создана!")
                else:
                    error_text = await resp.text()
                    await message.answer(
                        f"❌ Ошибка при создании задачи\n"
                        f"Код: {resp.status}\n"
                        f"Детали: {error_text[:200]}"
                    )
    except Exception as e:
        await message.answer(f"❌ Ошибка подключения к API: {str(e)}")
    
    await state.clear()


@router.message(Command("complete"))
async def cmd_complete(message: Message):
    """Завершить задачу"""
    telegram_id = message.from_user.id
    command_parts = message.text.split()
    
    # Если указан ID задачи
    if len(command_parts) >= 2:
        try:
            task_id = int(command_parts[1])
        except ValueError:
            await message.answer("❌ Неверный формат. Используйте: /complete <ID_задачи>")
            return
        
        # Завершаем задачу по ID
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/tasks/{task_id}/complete",
                params={"telegram_id": telegram_id}
            ) as resp:
                if resp.status == 200:
                    task = await resp.json()
                    # Форматируем время
                    completed_at = task.get('completed_at')
                    if completed_at:
                        try:
                            dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                            # Конвертируем в локальное время (UTC+3 для примера, можно настроить)
                            formatted_time = dt.strftime('%d.%m.%Y %H:%M')
                        except:
                            formatted_time = completed_at
                    else:
                        formatted_time = "только что"
                    
                    await message.answer(
                        f"✅ Задача завершена!\n\n"
                        f"📝 {task['title']}\n"
                        f"🕐 Завершена: {formatted_time}"
                    )
                elif resp.status == 404:
                    await message.answer("❌ Задача не найдена или уже завершена")
                else:
                    error_text = await resp.text()
                    await message.answer(
                        f"❌ Ошибка при завершении задачи\n"
                        f"Код: {resp.status}\n"
                        f"Детали: {error_text[:200]}"
                    )
        return
    
    # Если ID не указан, показываем список незавершенных задач
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/tasks", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                tasks = data.get("items", [])
                
                # Фильтруем только незавершенные задачи
                pending_tasks = [t for t in tasks if t["status"] in ["pending", "in_progress"]]
                
                if not pending_tasks:
                    await message.answer("✅ У вас нет незавершенных задач!")
                    return
                
                # Показываем список задач с ID
                text = "📋 Ваши незавершенные задачи:\n\n"
                for task in pending_tasks[:10]:
                    status_emoji = {
                        "pending": "⏳",
                        "in_progress": "🔄"
                    }
                    emoji = status_emoji.get(task["status"], "📝")
                    text += f"{emoji} [{task['id']}] {task['title']}\n"
                
                text += "\n💡 Для завершения отправьте: /complete <ID_задачи>"
                text += f"\nНапример: /complete {pending_tasks[0]['id']}"
                
                await message.answer(text)
            else:
                await message.answer("❌ Ошибка при получении задач")


@router.message(Command("start_task"))
async def cmd_start_task(message: Message):
    """Начать работу над задачей (перевести в статус in_progress)"""
    telegram_id = message.from_user.id
    command_parts = message.text.split()
    
    # Если указан ID задачи
    if len(command_parts) >= 2:
        try:
            task_id = int(command_parts[1])
        except ValueError:
            await message.answer("❌ Неверный формат. Используйте: /start_task <ID_задачи>")
            return
        
        # Обновляем статус задачи на in_progress
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{API_URL}/tasks/{task_id}",
                params={"telegram_id": telegram_id},
                json={"status": "in_progress"}
            ) as resp:
                if resp.status == 200:
                    task = await resp.json()
                    await message.answer(
                        f"🔄 Задача переведена в работу!\n\n"
                        f"📝 {task['title']}\n"
                        f"📊 Статус: В работе"
                    )
                elif resp.status == 404:
                    await message.answer("❌ Задача не найдена")
                else:
                    error_text = await resp.text()
                    await message.answer(
                        f"❌ Ошибка при обновлении задачи\n"
                        f"Код: {resp.status}\n"
                        f"Детали: {error_text[:200]}"
                    )
        return
    
    # Если ID не указан, показываем список задач в ожидании
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/tasks", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                data = await resp.json()
                tasks = data.get("items", [])
                
                # Фильтруем только задачи в ожидании
                pending_tasks = [t for t in tasks if t["status"] == "pending"]
                
                if not pending_tasks:
                    await message.answer("✅ У вас нет задач в ожидании!")
                    return
                
                # Показываем список задач с ID
                text = "📋 Задачи в ожидании:\n\n"
                for task in pending_tasks[:10]:
                    text += f"⏳ [{task['id']}] {task['title']}\n"
                
                text += "\n💡 Для начала работы отправьте: /start_task <ID_задачи>"
                text += f"\nНапример: /start_task {pending_tasks[0]['id']}"
                
                await message.answer(text)
            else:
                await message.answer("❌ Ошибка при получении задач")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Показать статистику"""
    telegram_id = message.from_user.id
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/stats", params={"telegram_id": telegram_id}) as resp:
            if resp.status == 200:
                stats = await resp.json()
                text = (
                    f"📊 Статистика:\n\n"
                    f"Всего: {stats['total']}\n"
                    f"✅ Выполнено: {stats['completed']}\n"
                    f"⏳ В ожидании: {stats['pending']}\n"
                    f"🔄 В работе: {stats['in_progress']}"
                )
                await message.answer(text)
            else:
                await message.answer("❌ Ошибка при получении статистики")

