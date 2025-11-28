import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)


def main():
    purchase_log_path = get_path('purchase_log.txt')
    visit_log_path = get_path('visit_log.csv')
    funnel_path = get_path('funnel.csv')

    purchases = {}
    
    if os.path.exists(purchase_log_path):
        with open(purchase_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    user_id = data.get('user_id')
                    category = data.get('category')
                    
                    if user_id and category:
                        purchases[user_id] = category
                except json.JSONDecodeError:
                    continue
    else:
        print(f"Файл {purchase_log_path} не найден.")
        return

    if os.path.exists(visit_log_path):
        with open(visit_log_path, 'r', encoding='utf-8') as f_visit, \
             open(funnel_path, 'w', encoding='utf-8', newline='') as f_funnel:
            
            reader = csv.reader(f_visit)
            writer = csv.writer(f_funnel)
            
            try:
                header = next(reader)
            except StopIteration:
                print(f"Файл {visit_log_path} пуст.")
                return

            writer.writerow(['user_id', 'source', 'category'])
            
            for row in reader:
                if not row:
                    continue
                
                if len(row) >= 1:
                    user_id = row[0]
                    
                    if user_id in purchases:
                        category = purchases[user_id]
                        source = row[1] if len(row) > 1 else ''
                        writer.writerow([user_id, source, category])
        
        print(f"Готово. Результат записан в {funnel_path}")
    else:
        print(f"Файл {visit_log_path} не найден.")

if __name__ == '__main__':
    main()
