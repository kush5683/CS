from random import randint
from castle_piece import Piece


def generate_castle_file():
    types = {0: "door", 1: "wall", 2: "lookout"}
    pieces = []
    door = Piece("door", randint(1, 10), randint(1, 10), randint(1, 10))
    lookout = Piece("lookout", randint(1, 10), randint(1, 10), randint(1, 10))
    pieces.append(str(door))
    pieces.append(str(lookout))
    number_of_additional_pieces = randint(0, 10)
    while len(pieces) < number_of_additional_pieces+1:
        piece = Piece(types[randint(0, 2)], randint(1, 10), randint(1, 10), randint(1, 10))
        pieces.append(str(piece))
    with open("castle.txt", "w") as castle_file:
        for piece in pieces:
            p = piece.split(",")
            for attr in p:
                castle_file.write(attr.strip() + "\t")
            castle_file.write("\n")

if __name__ == "__main__":
    generate_castle_file()
