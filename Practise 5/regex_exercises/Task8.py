import re
pattern = r"(?=[A-Z])"  # Positive lookahead for uppercase
test_str = "HelloWorldPython"
parts = re.split(pattern, test_str)
print(parts)  # ['', 'Hello', 'World', 'Python']