import re
pattern = r"(?<!^)(?=[A-Z])"
test_str = "helloWorldPython"
snake_case = re.sub(pattern, "_", test_str).lower()
print(snake_case)  # hello_world_python