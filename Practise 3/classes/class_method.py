

class MathOperations:

    @staticmethod
    def add(a, b):
        return a + b

    @classmethod
    def description(cls):
        return f"This is {cls.__name__} class"

print(MathOperations.add(5, 3))
print(MathOperations.description())