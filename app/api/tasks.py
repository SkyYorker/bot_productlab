"""
API endpoints для задач
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.services.user_service import UserService
from app.core.database import get_db
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from app.services.task_service import TaskService
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Rate limiter (будет инициализирован в main.py)
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    username: Optional[str] = Query(None, description="Username пользователя"),
    first_name: Optional[str] = Query(None, description="Имя пользователя"),
    last_name: Optional[str] = Query(None, description="Фамилия пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую задачу"""
    task = await TaskService.create_task(
        db, task_data, telegram_id, username, first_name, last_name
    )
    return task


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список задач с пагинацией"""
    # Получаем пользователя по telegram_id
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        return TaskListResponse(items=[], total=0, page=page, page_size=page_size, pages=0)
    
    tasks, total = await TaskService.get_tasks(db, user.id, status, page, page_size)
    
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return TaskListResponse(
        items=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Получить задачу по ID"""
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    task = await TaskService.get_task(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Обновить задачу"""
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    task = await TaskService.update_task(db, task_id, user.id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Удалить задачу"""
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = await TaskService.delete_task(db, task_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Завершить задачу"""
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    task = await TaskService.complete_task(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

