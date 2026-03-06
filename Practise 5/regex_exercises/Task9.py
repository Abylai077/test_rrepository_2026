import re
pattern = r"(?<!^)(?=[A-Z])"
test_str = "HelloWorldPython"
new_str = re.sub(pattern, " ", test_str)
print(new_str)  # Hello World Python