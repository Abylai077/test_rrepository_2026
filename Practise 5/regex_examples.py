import re
print(re.search(r"\d+", "Price: 12.5"))  # First number

print(re.findall(r"\d+\.\d+", "Milk 2.5, Bread 1.2") ) # ['2.5', '1.2']

print(re.split(r"\s*,\s*", "Milk, Bread, Eggs") ) # ['Milk', 'Bread', 'Eggs']

print(re.sub(r"\d+", "#", "Price 12 34") ) # "Price # #"

print(re.sub(r"\d+", "#", "Price 12 34"))  # "Price # #"

print(re.match(r"Price", "Price: 12.5"))  # Only at start