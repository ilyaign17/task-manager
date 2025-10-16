from __future__ import annotations

from typing import List, Optional

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app import models
from app.enums import TaskStatus
from app.schemas import TaskCreate, TaskUpdate


# Локальный алиас для удобства тайпинга
Task = models.Task


def create_task(db: Session, data: TaskCreate) -> Task:
    """
    Создать задачу и вернуть ORM-объект.
    Гарантирует откат транзакции при исключениях.
    """
    task = Task(title=data.title, description=data.description, status=data.status)
    try:
        db.add(task)
        db.commit()        # фиксируем INSERT
        db.refresh(task)   # получаем сгенерированный uuid
        return task
    except Exception:
        db.rollback()
        raise


def get_task(db: Session, uuid: str) -> Optional[Task]:
    """Получить задачу по UUID или None."""
    stmt = select(Task).where(Task.uuid == uuid)
    return db.execute(stmt).scalar_one_or_none()


def get_tasks(db: Session, status: Optional[TaskStatus] = None) -> List[Task]:
    """
    Список задач с опц. фильтром по статусу.
    Сортировка выполняется на стороне БД: статус → title (case-insensitive).
    Порядок статусов: CREATED → IN_PROGRESS → DONE.
    """
    # CASE-мэппинг для детерминированного порядка статусов
    status_order = case(
        (models.Task.status == TaskStatus.CREATED, 0),
        (models.Task.status == TaskStatus.IN_PROGRESS, 1),
        (models.Task.status == TaskStatus.DONE, 2),
        else_=3,
    )
    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)

    stmt = stmt.order_by(status_order, func.lower(Task.title))
    return list(db.execute(stmt).scalars().all())


def update_task(db: Session, uuid: str, data: TaskUpdate) -> Optional[Task]:
    """
    Частичное обновление; возвращает обновлённую задачу или None, если не найдена.
    """
    task = get_task(db, uuid)
    if not task:
        return None

    # Обновляем только переданные поля
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status

    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise


def delete_task(db: Session, uuid: str) -> bool:
    """Удаление по UUID. True — удалили, False — не нашли."""
    task = get_task(db, uuid)
    if not task:
        return False

    try:
        db.delete(task)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
