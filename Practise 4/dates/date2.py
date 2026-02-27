import datetime
x = datetime.datetime.now()
today = x
yesterday = x - datetime.timedelta(days=1)
tomorrow = x + datetime.timedelta(days =1)
print("Today:", x)
print("Yesterday:", yesterday)
print("tomorrow:", tomorrow)