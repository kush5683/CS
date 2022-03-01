from random import choice as randchoice
from random import seed as randseed
from os import remove


def validate(filename):
    has_goal = False
    has_start = False
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if has_goal and has_start:
                return True
            for char in line:
                if char == 'G':
                    has_goal = True
                if char == 'S':
                    has_start = True
    return False


def main(size=6, version=1):
    start_placed = False
    goal_placed = False
    wait_till_next_row = False
    filename = f'boards/board-{size}x{size}_{version}.txt'
    with open(filename, 'w') as f:
        for i in range(size):
            for j in range(size):
                numbers = [-2, -2, -2, -2, -1, -1, -1 - 1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                choice = randchoice(numbers)
                if choice == -2 and not start_placed and not wait_till_next_row:
                    if j == size - 1:
                        f.write("S")
                    else:
                        f.write("S\t")
                    start_placed = True
                    wait_till_next_row = True
                    continue
                elif choice == -1 and not goal_placed and not wait_till_next_row:
                    if j == size - 1:
                        f.write("G")
                    else:
                        f.write("G\t")
                    goal_placed = True
                    continue
                while choice == -2 or choice == -1:
                    choice = randchoice(numbers)
                if j == size - 1:
                    f.write(f"{choice}")
                else:
                    f.write(f"{choice}\t")

            f.write("\n")
            wait_till_next_row = False
    if not validate(filename):
        remove(filename)


if __name__ == "__main__":
    for i in range(5000):
        main(6, i)
