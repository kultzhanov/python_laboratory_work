documents = [
    {'type': 'passport', 'number': '2207 876234', 'name': 'Василий Гупкин'},
    {'type': 'invoice',  'number': '11-2',       'name': 'Геннадий Покемонов'},
    {'type': 'insurance','number': '10006',      'name': 'Аристарх Павлов'}
]

directories = {
    '1': ['2207 876234', '11-2'],
    '2': ['10006'],
    '3': []
}


def get_owner_by_number(doc_number: str, docs: list) -> str | None:
    for doc in docs:
        if doc.get('number') == doc_number:
            return doc.get('name')
    return None


def handle_print_owner():
    doc_number = input("Введите номер документа: ")
    owner = get_owner_by_number(doc_number, documents)
    if owner is not None:
        print(f"Владелец документа: {owner}")
    else:
        print("Документ с таким номером не найден.")


def main():
    while True:
        command = input("Введите команду: ")

        if command == 'q':
            print("Выход из программы.")
            break

        elif command == 'p':
            handle_print_owner()

        else:
            print("Неизвестная команда. Доступные команды: p, q")


if __name__ == "__main__":
    main()