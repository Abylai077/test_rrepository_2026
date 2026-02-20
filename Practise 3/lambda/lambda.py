# Example 1
is_positive = lambda x: x > 0

# Example 2
numbers = [10, 15, 20]
greater_than_12 = list(filter(lambda x: x > 12, numbers))

# Example 3
celsius = [0, 20, 30]
fahrenheit = list(map(lambda c: (c * 9/5) + 32, celsius))

# Example 4
pairs = [(1, 3), (2, 2), (4, 1)]
sorted_pairs = sorted(pairs, key=lambda x: x[1])

# Example 5
multiply = lambda a, b: a * b

print(is_positive(5))
print(greater_than_12)
print(fahrenheit)
print(sorted_pairs)
print(multiply(3, 4))