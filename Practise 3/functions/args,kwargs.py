
# Example 1: *args
def add_all(*numbers):
    """Adds unlimited numbers."""
    return sum(numbers)

print(add_all(1, 2, 3, 4))


# Example 2: Looping *args
def show_args(*args):
    for arg in args:
        print(arg)

show_args("Python", "Java", "C++")


# Example 3: **kwargs
def show_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

show_info(name="Alice", age=25)


# Example 4: Combined
def combined(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

combined(1, 2, name="Bob")