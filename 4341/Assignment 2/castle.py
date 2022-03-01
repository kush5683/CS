from castle_piece import Piece
from random import randint, choice


class Castle:
    def __init__(self, pieces, all_pieces):
        self.selection_probability = None
        self.pieces = pieces
        self.total_cost = sum([piece.cost for piece in pieces])
        self.all_pieces = all_pieces
        self.validate()

    def __repr__(self):
        rep = ""
        for piece in self.pieces:
            rep += f"{piece}\n"
        rep += f"Total cost: {self.total_cost}\n"
        return rep

    def __gt__(self, other):
        return self.fitness() > other.fitness()

    def validate(self):
        """

        make sure just one door

        """
        door_count = list(filter(lambda p: p.type == "door", self.pieces))
        lookout_count = list(filter(lambda p: p.type == "lookout", self.pieces))
        if len(door_count) > 1:
            while len(door_count) > 1:
                to_remove = choice(door_count)
                self.pieces.remove(to_remove)
                door_count.remove(to_remove)
        elif len(door_count) == 0:
            self.pieces.append([p for p in self.all_pieces if p.type == "door"][0])
        if len(lookout_count) > 1:
            while len(lookout_count) > 1:
                to_remove = choice(lookout_count)
                self.pieces.remove(to_remove)
                lookout_count.remove(to_remove)
        elif len(lookout_count) == 0:
            self.pieces.append([p for p in self.all_pieces if p.type == "lookout"][0])

    def zero_fitness_condition(self):
        max_height = self.pieces[0].strength
        if len(self.pieces) > max_height:
            return False
        previous_piece = self.pieces[0]
        for piece in self.pieces:
            if piece.width > previous_piece.width:
                return False
        if self.pieces[0].type != "door" or self.pieces[-1].type != "lookout":
            return False
        return True

    def fitness(self):
        if self.zero_fitness_condition():
            return 10 + (len(self.pieces) ** 2) - self.total_cost
        else:
            return 0

    def mutate(self):
        piece_A = choice(self.pieces)
        piece_B = choice(self.pieces)
        self.pieces[self.pieces.index(piece_A)] = piece_B
        self.pieces[self.pieces.index(piece_B)] = piece_A

    def set_selection_probability(self, selection_probablity):
        self.selection_probability = selection_probablity

    def crossover(self, other):
        child_one = Castle(self.pieces.copy()[:len(self.pieces) // 2] + other.pieces.copy()[len(self.pieces) // 2:],
                           self.all_pieces)
        child_two = Castle(other.pieces.copy()[:len(other.pieces) // 2] + self.pieces.copy()[len(other.pieces) // 2:],
                           self.all_pieces)
        return child_one, child_two
