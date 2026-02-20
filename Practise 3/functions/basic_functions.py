

# 1: Simple function
def greet():
    """Prints a welcome message."""
    print("Welcome to Python!")

greet()


# 2: Function with parameter
def greet_user(name):
    """Greets a user by name."""
    print(f"Hello, {name}!")

greet_user("Alice")


# 3: Passing list as argument
def print_list(items):
    """Prints each item from a list."""
    for item in items:
        print(item)

print_list(["Apple", "Banana", "Cherry"])


# 4 Function with multiple parameters
def calculate_area(length, width):
    """Returns area of a rectangle."""
    return length * width

print("Area:", calculate_area(5, 3))