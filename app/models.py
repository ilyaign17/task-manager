import uuid as _uuid
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.enums import TaskStatus

class Task(Base):
    __tablename__ = "tasks"

    uuid: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(_uuid.uuid4()),
        doc="Первичный ключ задачи (UUID4)."
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Заголовок задачи (обязателен)."
    )
    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
        doc="Опциональное описание."
    )
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.CREATED,
        doc="Статус: создано | в работе | завершено."
    )
