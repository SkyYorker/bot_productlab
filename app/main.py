"""
Главный файл FastAPI приложения
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import engine, Base
from app.api import tasks, stats

# Создание приложения
app = FastAPI(
    title="Task Management API",
    description="API для управления задачами с Telegram ботом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(tasks.router)
app.include_router(stats.router)


@app.on_event("startup")
async def startup():
    """Инициализация при старте"""
    # Создание таблиц (в продакшене используйте миграции)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass


@app.on_event("shutdown")
async def shutdown():
    """Очистка при завершении"""
    await engine.dispose()


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok"}

