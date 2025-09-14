ticket = input("Введи номер билета: ")

if len(ticket) == 6:
    left_sum = int(ticket[0]) + int(ticket[1]) + int(ticket[2])
    right_sum = int(ticket[3]) + int(ticket[4]) + int(ticket[5])
    
    if left_sum == right_sum:
        print("Счастливый")
    else:
        print("Несчастливый")
