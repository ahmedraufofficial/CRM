from datetime import datetime

a = "23/11/2021 13:19:32"
print(a[0:6]+a[8:])
b = datetime.strptime(a, '%d/%m/%y %H:%M:%S')
print(b)