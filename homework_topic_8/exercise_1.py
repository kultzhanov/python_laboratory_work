import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from werkzeug.utils import secure_filename

# Настраиваем путь к шаблонам относительно файла
TEMPLATE_FOLDER = Path(__file__).parent / 'templates'

app = Flask(__name__, template_folder=str(TEMPLATE_FOLDER))
app.secret_key = os.urandom(24)

# Глобальная переменная для хранения токена (вводится пользователем при запуске)
YANDEX_TOKEN = None

# Папка для локальных файлов
UPLOAD_FOLDER = Path(__file__).parent / 'files_to_upload'
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Папка на Яндекс.Диске для загрузки
YANDEX_DISK_FOLDER = '/homework_uploads'

# Базовый URL API Яндекс.Диска
YANDEX_API_BASE = 'https://cloud-api.yandex.net/v1/disk'


def get_headers():
    """Возвращает заголовки для API запросов."""
    return {'Authorization': f'OAuth {YANDEX_TOKEN}'}


def get_uploaded_files():
    """
    Получает список файлов, уже загруженных на Яндекс.Диск.
    Обрабатывает пагинацию для получения всех файлов.
    
    Returns:
        set: Множество имен загруженных файлов
    """
    uploaded_files = set()
    
    if not YANDEX_TOKEN:
        return uploaded_files
    
    # Сначала проверяем/создаем папку на Яндекс.Диске
    create_folder_if_not_exists()
    
    limit = 100  # Максимум файлов за один запрос
    offset = 0
    
    while True:
        url = f'{YANDEX_API_BASE}/resources'
        params = {
            'path': YANDEX_DISK_FOLDER,
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = requests.get(url, headers=get_headers(), params=params)
            
            if response.status_code == 404:
                # Папка не существует - нет загруженных файлов
                break
            
            response.raise_for_status()
            data = response.json()
            
            # Получаем список элементов в папке
            items = data.get('_embedded', {}).get('items', [])
            
            for item in items:
                if item.get('type') == 'file':
                    uploaded_files.add(item.get('name'))
            
            # Проверяем, есть ли еще файлы
            total = data.get('_embedded', {}).get('total', 0)
            offset += limit
            
            if offset >= total:
                break
                
        except requests.exceptions.RequestException as e:
            print(f'Ошибка при получении списка файлов: {e}')
            break
    
    return uploaded_files


def create_folder_if_not_exists():
    """Создает папку на Яндекс.Диске, если она не существует."""
    url = f'{YANDEX_API_BASE}/resources'
    params = {'path': YANDEX_DISK_FOLDER}
    
    try:
        # Проверяем существование папки
        response = requests.get(url, headers=get_headers(), params=params)
        
        if response.status_code == 404:
            # Создаем папку
            response = requests.put(url, headers=get_headers(), params=params)
            if response.status_code in (201, 409):  # 409 - папка уже существует
                return True
            response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f'Ошибка при создании папки: {e}')
        return False


def upload_file_to_yandex(file_path):
    """
    Загружает файл на Яндекс.Диск.
    
    Args:
        file_path: Путь к локальному файлу
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if not YANDEX_TOKEN:
        return False, 'Токен не установлен'
    
    file_name = os.path.basename(file_path)
    yandex_path = f'{YANDEX_DISK_FOLDER}/{file_name}'
    
    # Получаем URL для загрузки
    url = f'{YANDEX_API_BASE}/resources/upload'
    params = {
        'path': yandex_path,
        'overwrite': 'true'
    }
    
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        
        upload_url = response.json().get('href')
        
        if not upload_url:
            return False, 'Не удалось получить URL для загрузки'
        
        # Загружаем файл
        with open(file_path, 'rb') as f:
            upload_response = requests.put(upload_url, files={'file': f})
        
        if upload_response.status_code in (201, 202):
            return True, f'Файл "{file_name}" успешно загружен'
        else:
            return False, f'Ошибка загрузки: {upload_response.status_code}'
            
    except requests.exceptions.RequestException as e:
        return False, f'Ошибка при загрузке файла: {e}'


def get_local_files():
    """Возвращает список локальных файлов в папке для загрузки."""
    files = []
    if UPLOAD_FOLDER.exists():
        for item in UPLOAD_FOLDER.iterdir():
            if item.is_file():
                files.append({
                    'name': item.name,
                    'path': str(item),
                    'size': item.stat().st_size
                })
    return sorted(files, key=lambda x: x['name'])


def format_file_size(size_bytes):
    """Форматирует размер файла в читаемый вид."""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
        if size_bytes < 1024.0:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024.0
    return f'{size_bytes:.1f} ТБ'


@app.route('/')
def index():
    """Главная страница со списком файлов."""
    files = get_local_files()
    
    # Добавляем отформатированный размер
    for file in files:
        file['size_formatted'] = format_file_size(file['size'])
    
    # Получаем список загруженных файлов с Яндекс.Диска
    uploaded_files = get_uploaded_files()
    
    # Получаем flash сообщения
    messages = []
    with app.test_request_context():
        for category in ['success', 'error']:
            for message in request.args.getlist(f'msg_{category}'):
                messages.append((category, message))
    
    return render_template(
        'index.html',
        files=files,
        uploaded_files=uploaded_files,
        yandex_folder=YANDEX_DISK_FOLDER,
        messages=messages
    )


@app.route('/add-file', methods=['POST'])
def add_file():
    """Добавление локального файла в папку для загрузки."""
    if 'file' not in request.files:
        return redirect(url_for('index', msg_error='Файл не выбран'))
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index', msg_error='Файл не выбран'))
    
    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename
    file.save(str(file_path))
    
    return redirect(url_for('index', msg_success=f'Файл "{filename}" добавлен'))


@app.route('/upload', methods=['POST'])
def upload():
    """Загрузка файла на Яндекс.Диск."""
    file_path = request.form.get('file_path')
    
    if not file_path or not os.path.exists(file_path):
        return redirect(url_for('index', msg_error='Файл не найден'))
    
    success, message = upload_file_to_yandex(file_path)
    
    if success:
        return redirect(url_for('index', msg_success=message))
    else:
        return redirect(url_for('index', msg_error=message))


def main():
    """Главная функция запуска сервера."""
    global YANDEX_TOKEN
    
    print('=' * 60)
    print('  Сервер загрузки файлов на Яндекс.Диск')
    print('=' * 60)
    print()
    print('Для работы с Яндекс.Диском необходим OAuth токен.')
    print('Получить токен можно на: https://yandex.ru/dev/disk/poligon/')
    print()
    
    # Запрашиваем токен у пользователя
    while True:
        token = input('Введите OAuth токен Яндекс.Диска: ').strip()
        if token:
            YANDEX_TOKEN = token
            break
        print('Токен не может быть пустым. Попробуйте снова.')
    
    # Проверяем токен
    print('\nПроверка токена...')
    try:
        response = requests.get(
            f'{YANDEX_API_BASE}/',
            headers=get_headers()
        )
        if response.status_code == 200:
            user_info = response.json().get('user', {})
            print(f'✓ Токен действителен. Пользователь: {user_info.get("display_name", "Неизвестно")}')
        else:
            print(f'✗ Ошибка проверки токена: {response.status_code}')
            print('  Проверьте правильность токена и попробуйте снова.')
            return
    except requests.exceptions.RequestException as e:
        print(f'✗ Ошибка подключения: {e}')
        return
    
    # Создаем папку для загрузки на Яндекс.Диске
    print(f'\nСоздание папки "{YANDEX_DISK_FOLDER}" на Яндекс.Диске...')
    if create_folder_if_not_exists():
        print('✓ Папка готова')
    
    # Создаем локальную папку для файлов
    print(f'\nЛокальная папка для файлов: {UPLOAD_FOLDER}')
    
    print()
    print('=' * 60)
    print('  Сервер запущен: http://127.0.0.1:5000')
    print('  Для остановки нажмите Ctrl+C')
    print('=' * 60)
    print()
    
    # Запускаем сервер
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == '__main__':
    main()
