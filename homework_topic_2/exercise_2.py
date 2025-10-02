# Задание 2
boys = ['Peter', 'Alex', 'John', 'Arthur', 'Richard']
girls = ['Kate', 'Liza', 'Kira', 'Emma', 'Trisha']

boys_sorted = sorted(boys)
girls_sorted = sorted(girls)

if len(boys_sorted) == len(girls_sorted):
    print("идеальные пары:")
    for b, g in zip(boys_sorted, girls_sorted):
        print(f"{b} и {g}")
else:
    print("кто-то может остаться без пары")