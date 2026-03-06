import re
def snake_to_camel(s):
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])

test_str = "hello_world_example"
print( snake_to_camel(test_str))  # helloWorldExample