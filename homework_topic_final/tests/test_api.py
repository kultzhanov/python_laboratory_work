import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import httpx
    USE_HTTPX = True
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    USE_HTTPX = False

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def make_request(method: str, path: str, data: dict = None) -> tuple[int, any]:
    url = f"{BASE_URL}{path}"
    
    if USE_HTTPX:
        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            
            body = response.json() if response.text else None
            return response.status_code, body
    else:
        req = Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        
        body_bytes = None
        if data:
            body_bytes = json.dumps(data).encode('utf-8')
        
        try:
            with urlopen(req, body_bytes) as response:
                response_body = response.read().decode('utf-8')
                return response.status, json.loads(response_body) if response_body else None
        except HTTPError as e:
            return e.code, None


def test_health():
    print("\n🏥 Тест: Health Check")
    print("-" * 40)
    
    status, response = make_request("GET", "/health")
    
    print(f"Запрос: GET /health")
    print(f"Статус: {status}")
    print(f"Ответ: {response}")
    
    assert status == 200, f"Ожидался статус 200, получен {status}"
    assert response["status"] == "ok"
    
    print("✅ Тест пройден!")


def test_create_task():
    print("\n📝 Тест: Создание задачи")
    print("-" * 40)
    
    task_data = {"title": "Тестовая задача", "priority": "high"}
    status, response = make_request("POST", "/tasks", task_data)
    
    print(f"Запрос: POST /tasks")
    print(f"Тело: {task_data}")
    print(f"Статус: {status}")
    print(f"Ответ: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    assert status == 201, f"Ожидался статус 201, получен {status}"
    assert response["title"] == "Тестовая задача"
    assert response["priority"] == "high"
    assert response["isDone"] == False
    assert "id" in response
    
    print("✅ Тест пройден!")
    return response["id"]


def test_get_tasks():
    print("\n📋 Тест: Получение списка задач")
    print("-" * 40)
    
    status, response = make_request("GET", "/tasks")
    
    print(f"Запрос: GET /tasks")
    print(f"Статус: {status}")
    print(f"Количество задач: {len(response)}")
    
    assert status == 200, f"Ожидался статус 200, получен {status}"
    assert isinstance(response, list)
    
    print("✅ Тест пройден!")
    return response


def test_complete_task(task_id: int):
    print(f"\n✔️  Тест: Отметка задачи {task_id} выполненной")
    print("-" * 40)
    
    status, _ = make_request("POST", f"/tasks/{task_id}/complete")
    
    print(f"Запрос: POST /tasks/{task_id}/complete")
    print(f"Статус: {status}")
    
    assert status == 200, f"Ожидался статус 200, получен {status}"
    
    print("✅ Тест пройден!")


def test_complete_nonexistent_task():
    print("\n❌ Тест: Отметка несуществующей задачи")
    print("-" * 40)
    
    status, _ = make_request("POST", "/tasks/99999/complete")
    
    print(f"Запрос: POST /tasks/99999/complete")
    print(f"Статус: {status}")
    
    assert status == 404, f"Ожидался статус 404, получен {status}"
    
    print("✅ Тест пройден!")


def main():
    print("=" * 60)
    print("  Task Manager API Tests")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print(f"HTTP Client: {'httpx' if USE_HTTPX else 'urllib'}")
    
    try:
        test_health()
        task_id = test_create_task()
        test_get_tasks()
        test_complete_task(task_id)
        
        _, tasks = make_request("GET", "/tasks")
        completed = next((t for t in tasks if t["id"] == task_id), None)
        assert completed["isDone"] == True, "Задача должна быть выполнена"
        
        test_complete_nonexistent_task()
        
        print("\n" + "=" * 60)
        print("  ✅ Все тесты пройдены успешно!")
        print("=" * 60)
        
    except ConnectionRefusedError:
        print("\n❌ Ошибка: Сервер не запущен!")
        print(f"   Запустите: python main.py")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ Тест провален: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
