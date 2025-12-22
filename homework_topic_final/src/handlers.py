import json
import re
from http.server import BaseHTTPRequestHandler
from typing import Optional

from .models import Priority
from .storage import TaskStorage


class TaskAPIHandler(BaseHTTPRequestHandler):
    
    COMPLETE_PATTERN = re.compile(r'^/tasks/(\d+)/complete$')
    storage: TaskStorage = None
    
    def _send_json_response(self, data: any, status: int = 200) -> None:
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
    
    def _send_empty_response(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header('Content-Length', 0)
        self.end_headers()
    
    def _send_error_response(self, message: str, status: int = 400) -> None:
        self._send_json_response({"error": message}, status)
    
    def _read_json_body(self) -> Optional[dict]:
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        
        try:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    
    def do_GET(self) -> None:
        if self.path == '/tasks':
            self._handle_get_tasks()
        elif self.path == '/health':
            self._handle_health()
        else:
            self._send_error_response("Not Found", 404)
    
    def do_POST(self) -> None:
        if self.path == '/tasks':
            self._handle_create_task()
        else:
            match = self.COMPLETE_PATTERN.match(self.path)
            if match:
                task_id = int(match.group(1))
                self._handle_complete_task(task_id)
            else:
                self._send_error_response("Not Found", 404)
    
    def _handle_health(self) -> None:
        self._send_json_response({"status": "ok"})
    
    def _handle_get_tasks(self) -> None:
        tasks = self.storage.get_all()
        self._send_json_response([task.to_dict() for task in tasks])
    
    def _handle_create_task(self) -> None:
        body = self._read_json_body()
        
        if body is None:
            self._send_error_response("Invalid JSON body", 400)
            return
        
        title = body.get('title')
        priority = body.get('priority', Priority.NORMAL.value)
        
        if not title:
            self._send_error_response("Field 'title' is required", 400)
            return
        
        task = self.storage.create(title, priority)
        self._send_json_response(task.to_dict(), 201)
    
    def _handle_complete_task(self, task_id: int) -> None:
        if self.storage.complete(task_id):
            self._send_empty_response(200)
        else:
            self._send_empty_response(404)
    
    def log_message(self, format: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {args[0]}")
