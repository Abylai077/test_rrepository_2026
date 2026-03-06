import re
pattern = r"[A-Z][a-z]+"
test_str = "Python Java CSharp Ruby"
matches = re.findall(pattern, test_str)
print(matches)  # ['Python', 'Java', 'CSharp', 'Ruby']