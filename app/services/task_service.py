"""
Сервис для работы с задачами
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.user_service import UserService
from datetime import datetime


class TaskService:
    """Сервис для работы с задачами"""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_data: TaskCreate,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Task:
        """Создать новую задачу"""
        # Получаем или создаем пользователя
        user = await UserService.get_or_create_user(
            db, telegram_id, username, first_name, last_name
        )
        
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            user_id=user.id,  # Используем id из таблицы users
            status=TaskStatus.PENDING
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_task(
        db: AsyncSession,
        task_id: int,
        user_id: int
    ) -> Optional[Task]:
        """Получить задачу по ID"""
        result = await db.execute(
            select(Task)
            .where(and_(Task.id == task_id, Task.user_id == user_id, Task.is_deleted == False))
            .options(selectinload(Task.user))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        user_id: int,
        status: Optional[TaskStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[Task], int]:
        """Получить список задач с пагинацией"""
        query = select(Task).where(
            and_(Task.user_id == user_id, Task.is_deleted == False)
        )
        
        if status:
            query = query.where(Task.status == status)
        
        # Подсчет общего количества
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Получение задач с пагинацией
        query = query.order_by(Task.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query.options(selectinload(Task.user)))
        tasks = result.scalars().all()
        
        return tasks, total
    
    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Обновить задачу"""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        # Если статус меняется на completed, устанавливаем completed_at
        if update_data.get("status") == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: int,
        user_id: int
    ) -> bool:
        """Удалить задачу (мягкое удаление)"""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return False
        
        task.is_deleted = True
        await db.commit()
        return True
    
    @staticmethod
    async def complete_task(
        db: AsyncSession,
        task_id: int,
        user_id: int
    ) -> Optional[Task]:
        """Завершить задачу"""
        task = await TaskService.get_task(db, task_id, user_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """Получить статистику по задачам"""
        # Подсчет по статусам
        base_query = select(Task).where(
            and_(Task.user_id == user_id, Task.is_deleted == False)
        )
        
        # Общее количество
        total_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(Task.user_id == user_id, Task.is_deleted == False)
            )
        )
        total = total_result.scalar() or 0
        
        # Выполненные
        completed_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.COMPLETED,
                    Task.is_deleted == False
                )
            )
        )
        completed = completed_result.scalar() or 0
        
        # В ожидании
        pending_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.PENDING,
                    Task.is_deleted == False
                )
            )
        )
        pending = pending_result.scalar() or 0
        
        # В работе
        in_progress_result = await db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.IN_PROGRESS,
                    Task.is_deleted == False
                )
            )
        )
        in_progress = in_progress_result.scalar() or 0
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress
        }

