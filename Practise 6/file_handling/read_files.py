# Read entire file
with open("sample.txt", "r") as file:
    content = file.read()
    print("Full content:\n", content)

# Read line by line
with open("sample.txt", "r") as file:
    print("Line by line:")
    for line in file:
        print(line.strip())

# Read lines into list
with open("sample.txt", "r") as file:
    lines = file.readlines()
    print("Lines list:", lines)