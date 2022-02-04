from random import choice as randchoice
from random import seed as randseed


def main(size=6):
    start_placed = False
    goal_placed = False
    wait_till_next_row = False
    with open(f'board-{size}x{size}.txt', 'w') as f:
        for i in range(size):
            for j in range(size):
                numbers = [-2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                choice = randchoice(numbers)
                if choice == -2 and not start_placed and not wait_till_next_row:
                    if j == size-1:
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


if __name__ == "__main__":
    main(16)
