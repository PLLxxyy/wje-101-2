from enum import StrEnum


class RoastLevel(StrEnum):
    light = "light"
    medium = "medium"
    dark = "dark"


class UserRole(StrEnum):
    user = "user"
    admin = "admin"


class ProcessMethod(StrEnum):
    washed = "washed"
    natural = "natural"
    honey = "honey"
    anaerobic = "anaerobic"

