class Piece:
    def __init__(self, type, strength, width, cost):
        self.type = type.lower()
        self.strength = strength
        self.width = width
        self.cost = cost

    def __repr__(self):
        return f"{self.type}, {self.strength}, {self.width}, {self.cost}"

    def __eq__(self, other):
        return self.type == other.type and self.strength == other.strength and self.width == other.width and self.cost == other.cost

