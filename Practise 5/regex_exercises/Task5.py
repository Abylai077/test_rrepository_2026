import re
pattern = r"a.*b"
test_str = "acb a123b abb ab"
matches = re.findall(pattern, test_str)
print(matches)  # ['acb', 'a123b', 'abb', 'ab']