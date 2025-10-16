from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.enums import TaskStatus
from app import crud

# Группируем эндпойнты задач под общим префиксом и тегом OpenAPI
router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
    response_model_exclude_none=True,
)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskOut:
    """
    Создать новую задачу.

    - **payload**: данные задачи (заголовок, описание, статус и т.п.)
    - **returns**: созданная задача
    """
    return crud.create_task(db, payload)


@router.get(
    "/{uuid}",
    response_model=TaskOut,
    summary="Получить задачу по UUID",
    response_model_exclude_none=True,
)
def get_task(uuid: UUID, db: Session = Depends(get_db)) -> TaskOut:
    """
    Получить задачу по идентификатору.

    - **uuid**: UUID задачи
    - **returns**: задача, если найдена
    - **raises**: 404, если не найдена
    """
    task = crud.get_task(db, str(uuid))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.get(
    "",
    response_model=List[TaskOut],
    summary="Список задач (с фильтром по статусу)",
    response_model_exclude_none=True,
)
def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Фильтр по статусу"),
    db: Session = Depends(get_db),
) -> List[TaskOut]:
    """
    Получить список задач.

    - **status**: необязательный фильтр по статусу
    - **returns**: список задач (может быть пустым)
    """
    return crud.get_tasks(db, status)


@router.patch(
    "/{uuid}",
    response_model=TaskOut,
    summary="Обновить задачу (частично)",
    response_model_exclude_none=True,
)
def update_task(uuid: UUID, payload: TaskUpdate, db: Session = Depends(get_db)) -> TaskOut:
    """
    Частичное обновление полей задачи.

    - **uuid**: UUID задачи
    - **payload**: поля для обновления
    - **returns**: обновлённая задача
    - **raises**: 404, если не найдена
    """
    task = crud.update_task(db, str(uuid), payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.delete(
    "/{uuid}",
    status_code=204,
    response_class=Response,        # ← важно: не JSONResponse
    summary="Удалить задачу",
)
def delete_task(uuid: str, db: Session = Depends(get_db)):
    ok = crud.delete_task(db, uuid)
    if not ok:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return Response(status_code=204)  # ← без тела
