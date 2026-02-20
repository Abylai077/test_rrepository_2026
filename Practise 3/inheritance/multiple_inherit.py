
class Father:
    def skills(self):
        print("Gardening")

class Mother:
    def skills(self):
        print("Cooking")

class Child(Father, Mother):
    def show_skills(self):
        Father.skills(self)
        Mother.skills(self)

child = Child()
child.show_skills()