import re

pattern = r"ab*"
test_str = "abbb a abb aa"
matches = re.findall(pattern, test_str)
print( matches)  # ['abbb', 'a', 'abb', 'a', 'a']