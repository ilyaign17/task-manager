from enum import Enum


class TaskStatus(str, Enum):
    """
    Статусы задачи.

    Значения хранятся в БД и отдаются наружу как строки:
    - CREATED     → "создано"
    - IN_PROGRESS → "в работе"
    - DONE        → "завершено"
    """
    CREATED = "создано"
    IN_PROGRESS = "в работе"
    DONE = "завершено"
