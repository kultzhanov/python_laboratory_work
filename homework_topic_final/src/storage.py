import json
from pathlib import Path
from typing import Optional

from .models import Task, Priority


class TaskStorage:
    
    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        if not self._file_path.exists():
            return
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = Task.from_dict(task_data)
                    self._tasks[task.id] = task
                    if task.id >= self._next_id:
                        self._next_id = task.id + 1
            print(f"✓ Загружено {len(self._tasks)} задач из {self._file_path}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"✗ Ошибка загрузки задач: {e}")
    
    def _save(self) -> None:
        data = [task.to_dict() for task in self._tasks.values()]
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create(self, title: str, priority: str) -> Task:
        if priority not in [p.value for p in Priority]:
            priority = Priority.NORMAL.value
        
        task = Task(
            id=self._next_id,
            title=title,
            priority=priority,
            isDone=False
        )
        self._tasks[task.id] = task
        self._next_id += 1
        self._save()
        return task
    
    def get_all(self) -> list[Task]:
        return list(self._tasks.values())
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)
    
    def complete(self, task_id: int) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.isDone = True
        self._save()
        return True
