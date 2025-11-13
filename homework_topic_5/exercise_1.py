from datetime import datetime

dates = {
    'The Moscow Times': ('Wednesday, October 2, 2002', '%A, %B %d, %Y'),
    'The Guardian': ('Friday, 11.10.13', '%A, %d.%m.%y'),
    'Daily News': ('Thursday, 18 August 1977', '%A, %d %B %Y')
}

for newspaper, (date_str, fmt) in dates.items():
    dt = datetime.strptime(date_str, fmt)
    print(newspaper, '->', dt)