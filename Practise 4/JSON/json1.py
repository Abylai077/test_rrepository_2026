import json

data = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}

json_string = json.dumps(data)
print(json_string)