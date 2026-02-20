

class Car:
    wheels = 4  # Class variable

    def __init__(self, brand):
        self.brand = brand  # Instance variable

car1 = Car("Toyota")
car2 = Car("Honda")

print(car1.brand, "has", car1.wheels, "wheels")
print(car2.brand, "has", car2.wheels, "wheels")

# Changing class variable
Car.wheels = 6

print("After modification:")
print(car1.brand, "has", car1.wheels, "wheels")
print(car2.brand, "has", car2.wheels, "wheels")