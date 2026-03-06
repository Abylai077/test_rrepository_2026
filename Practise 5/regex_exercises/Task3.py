import re
pattern = r"[a-z]+_[a-z]+"
test_str = "hello_world python_program testCase"
matches = re.findall(pattern, test_str)
print( matches)  # ['hello_world', 'python_program']