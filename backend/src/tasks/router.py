import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database.connection import get_db
from src.database.models import User
from src.tasks.schemas import CompleteTaskResponse, HeatmapResponse, TaskResponse
from src.tasks.service import (
    TaskNotFoundError,
    complete_task,
    get_heatmap,
    get_todays_tasks,
)

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/today", response_model=list[TaskResponse])
async def today(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """Get today's tasks for the current program day."""
    tasks = await get_todays_tasks(db, user)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.post(
    "/{task_id}/complete",
    response_model=CompleteTaskResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_complete(
    task_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompleteTaskResponse:
    """Mark a task as completed, award XP, update streak, apply score drift."""
    try:
        result = await complete_task(db, task_id, user)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return CompleteTaskResponse(**result)


@router.get("/heatmap", response_model=HeatmapResponse)
async def heatmap(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HeatmapResponse:
    """Get 90-day completion heatmap."""
    data = await get_heatmap(db, user.id)
    return HeatmapResponse(**data)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: FastAPI router for task engine endpoints — today's tasks,
task completion, and heatmap data.

Flow:
1. GET /today — returns tasks for user's current program_day
2. POST /{task_id}/complete — completes a task with all side effects
3. GET /heatmap — returns 90-day completion grid

Main Entry Point: router (included in main.py)

Dependencies:
- src.tasks.service: business logic
- src.tasks.schemas: response models
- src.auth.dependencies: JWT auth
"""
