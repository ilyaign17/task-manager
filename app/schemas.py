from typing import Optional

from pydantic import BaseModel, Field

from app.enums import TaskStatus


class TaskCreate(BaseModel):
    """
    Схема входа для создания задачи.
    То, что клиент присылает в POST /tasks.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Заголовок задачи (обязателен, ≤200 символов)",
        examples=["Сходить в магазин"],
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Опциональное описание (≤2000 символов)",
        examples=["Купить хлеб и молоко"],
    )
    status: TaskStatus = Field(
        default=TaskStatus.CREATED,
        description="Статус при создании",
        examples=[TaskStatus.CREATED],
    )


class TaskUpdate(BaseModel):
    """
    Схема частичного обновления: PATCH /tasks/{uuid}.
    Любое поле можно опустить — меняем только переданные.
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Новый заголовок задачи (≤200 символов)",
        examples=["Позвонить клиенту"],
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Новое описание (≤2000 символов)",
        examples=["Созвониться до 18:00"],
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Новый статус задачи",
        examples=[TaskStatus.IN_PROGRESS],
    )


class TaskOut(BaseModel):
    """
    Схема ответа API (GET/POST/PATCH).
    """

    uuid: str = Field(description="UUID задачи")
    title: str = Field(description="Заголовок задачи")
    description: Optional[str] = Field(None, description="Описание задачи")
    status: TaskStatus = Field(description="Текущий статус задачи")

    class Config:
        from_attributes = True  # поддержка ORM-объектов
