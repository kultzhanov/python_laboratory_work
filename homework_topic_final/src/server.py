from http.server import HTTPServer
from pathlib import Path

from .config import Config
from .storage import TaskStorage
from .handlers import TaskAPIHandler


class TaskServer:
    
    def __init__(self, config: Config):
        self._config = config
        self._storage_path = Path(__file__).parent.parent / config.storage.file
        self._storage = TaskStorage(self._storage_path)
    
    def run(self) -> None:
        TaskAPIHandler.storage = self._storage
        
        host = self._config.server.host
        port = self._config.server.port
        
        server = HTTPServer((host, port), TaskAPIHandler)
        
        self._print_banner(host, port)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Сервер остановлен")
            server.shutdown()
    
    def _print_banner(self, host: str, port: int) -> None:
        print("=" * 60)
        print("  Task Manager API Server")
        print("=" * 60)
        print()
        print("Конфигурация:")
        print(f"  Host:         {host}")
        print(f"  Port:         {port}")
        print(f"  Storage:      {self._storage_path}")
        print()
        print(f"Сервер запущен: http://{host}:{port}")
        print()
        print("API endpoints:")
        print("  GET  /health             - проверка состояния")
        print("  GET  /tasks              - получить все задачи")
        print("  POST /tasks              - создать задачу")
        print("  POST /tasks/{id}/complete - выполнить задачу")
        print()
        print("Для остановки нажмите Ctrl+C")
        print("=" * 60)
        print()
