import json
from datetime import datetime

text = '{"name":"John", "birth":"1986-12-14", "city":"New York"}'

obj = json.loads(text)

obj["birth"] = datetime.strptime(obj["birth"], "%Y-%m-%d")

print(obj["name"], ",", obj["birth"])