"""
Тесты для API задач
"""

import pytest
from httpx import AsyncClient
from app.models.task import TaskStatus, TaskPriority


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Тест создания задачи"""
    response = await client.post(
        "/api/tasks?user_id=1",
        json={
            "title": "Тестовая задача",
            "description": "Описание задачи",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовая задача"
    assert data["status"] == TaskStatus.PENDING.value


@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient):
    """Тест получения списка задач"""
    # Создаем задачу
    await client.post(
        "/api/tasks?user_id=1",
        json={"title": "Задача 1", "priority": "medium"}
    )
    
    # Получаем список
    response = await client.get("/api/tasks?user_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient):
    """Тест завершения задачи"""
    # Создаем задачу
    create_response = await client.post(
        "/api/tasks?user_id=1",
        json={"title": "Задача для завершения", "priority": "low"}
    )
    task_id = create_response.json()["id"]
    
    # Завершаем задачу
    response = await client.post(f"/api/tasks/{task_id}/complete?user_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["completed_at"] is not None

