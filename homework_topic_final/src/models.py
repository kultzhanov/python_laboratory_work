from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class Task:
    title: str
    priority: str
    isDone: bool = False
    id: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "isDone": self.isDone
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id", 0),
            title=data.get("title", ""),
            priority=data.get("priority", Priority.NORMAL.value),
            isDone=data.get("isDone", False)
        )
