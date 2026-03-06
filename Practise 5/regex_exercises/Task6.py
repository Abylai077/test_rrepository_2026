import re
pattern = r"[ ,.]"
test_str = "Hello, world. This is Python"
new_str = re.sub(pattern, ":", test_str)
print(new_str)  # Hello::world::This:is:Python