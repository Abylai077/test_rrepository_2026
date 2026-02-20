
# Example 1: Simple return
def square(num):
    return num * num

print(square(5))


# Example 2: Returning multiple values
def min_max(numbers):
    """Returns minimum and maximum from list."""
    return min(numbers), max(numbers)

low, high = min_max([1, 8, 3, 6])
print("Min:", low, "Max:", high)


# Example 3: Boolean return
def is_even(num):
    return num % 2 == 0

print(is_even(10))


# Example 4: Early return
def check_number(num):
    if num < 0:
        return "Negative"
    return "Positive"

print(check_number(-5))