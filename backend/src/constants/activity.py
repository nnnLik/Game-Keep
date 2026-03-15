from enum import StrEnum


class ActivityActionType(StrEnum):
    GAME_CREATED = "game_created"
    FAVORITE_ADDED = "favorite_added"
    FAVORITE_REMOVED = "favorite_removed"
