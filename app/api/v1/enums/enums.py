from enum import Enum


class SortOrder(str, Enum):
    early = "asc"
    late = "desc"


class TicketStatusEnum(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"