"""
API endpoints для статистики
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.task_service import TaskService
from app.services.user_service import UserService
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/stats", tags=["stats"])

# Rate limiter (будет инициализирован в main.py)
limiter = Limiter(key_func=get_remote_address)


@router.get("")
async def get_statistics(
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику по задачам"""
    user = await UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        return {"total": 0, "completed": 0, "pending": 0, "in_progress": 0}
    
    stats = await TaskService.get_statistics(db, user.id)
    return stats

