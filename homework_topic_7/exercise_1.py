import csv
from pathlib import Path

def get_data_generator(file_path):
    if not file_path.exists():
        print(f"Файл {file_path} не найден.")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def get_device_name(device_type):
    devices = {
        'mobile': 'мобильного',
        'tablet': 'планшетного',
        'laptop': 'ноутбука',
        'desktop': 'настольного компьютера'
    }
    return devices.get(device_type, device_type)

def get_gender_attributes(sex):
    if sex == 'female':
        return {'adj': 'женского', 'verb': 'совершила'}
    return {'adj': 'мужского', 'verb': 'совершил'}

def transform_client_data(client_raw):
    sex_attrs = get_gender_attributes(client_raw.get('sex', ''))
    
    return {
        'name': client_raw.get('name', ''),
        'age': client_raw.get('age', ''),
        'bill': client_raw.get('bill', ''),
        'browser': client_raw.get('browser', ''),
        'region': client_raw.get('region', ''),
        'sex_adj': sex_attrs['adj'],
        'verb': sex_attrs['verb'],
        'device': get_device_name(client_raw.get('device_type', ''))
    }

def format_description(data):
    return (
        f"Пользователь {data['name']} {data['sex_adj']} пола, {data['age']} лет "
        f"{data['verb']} покупку на {data['bill']} у.е. с {data['device']} "
        f"браузера {data['browser']}. Регион, из которого совершалась покупка: {data['region']}."
    )

def main():
    base_dir = Path(__file__).parent.resolve()
    input_file = base_dir / 'web_clients_correct (1).csv'
    output_file = base_dir / 'descriptions.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for raw_row in get_data_generator(input_file):
            clean_data = transform_client_data(raw_row)
            description = format_description(clean_data)
            f_out.write(description + '\n')
            
    print(f"Обработка завершена. Результат: {output_file}")

if __name__ == '__main__':
    main()
