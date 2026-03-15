from enum import StrEnum


class GameStateEnum(StrEnum):
    BACKLOG = 'backlog'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'
