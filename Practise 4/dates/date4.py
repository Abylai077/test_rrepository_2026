from datetime import datetime

date_format = "%Y-%m-%d %H:%M:%S"

date1 = datetime.strptime(input("Enter first date: "), date_format)
date2 = datetime.strptime(input("Enter second date: "), date_format)

dif = date1 - date2

print(dif.total_seconds())