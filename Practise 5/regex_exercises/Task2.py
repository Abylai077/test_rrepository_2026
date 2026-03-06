import re
pattern = r"ab{2,3}"
test_str = "ab a abb abbb abbbb"
matches = re.findall(pattern, test_str)
print( matches)  # ['abb', 'abbb']