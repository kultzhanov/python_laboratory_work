# Задание 1
word = input("введите слово: ")

n = len(word)

if n % 2 == 0:
    middle = word[n//2 - 1:n//2 + 1]
else:
    middle = word[n//2]

print("результат: ", middle)