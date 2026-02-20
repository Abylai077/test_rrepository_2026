
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def info(self):
        print(f"Name: {self.name}, Breed: {self.breed}")

dog = Dog("Buddy", "Golden Retriever")
dog.info()