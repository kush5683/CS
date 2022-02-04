import agent
import board
from time import perf_counter

def main(filename, heuristic_number):
    """
    Main function.
    :return: 1 on success and 0 on failure.
    """
    # Create a board
    b = board.Board(filename)
    print(b)
    # Create an agent
    a = agent.Agent(b.get_start(), b.get_goal(), b)
    # print(a)
    start = perf_counter()
    a_star = a.a_star(heuristic_number)
    end = perf_counter()
    # print(f"Time taken:{end - start}")
    print(f"Score:{a_star[0]}")
    print(f"Number of actions:{a_star[1]}")
    print(f"Nodes expanded:{a_star[2]}")
    print(f"Actions:")
    for action in a_star[3][::-1][1:]:
        print(f"\t{action.lower()}")



if __name__ == "__main__":
    main('board.txt', 1)
