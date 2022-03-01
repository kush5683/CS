from matplotlib import pyplot as plt
from main import main
import os
from random import choice


def graph():
    all_boards = os.listdir('./boards')
    boards = []
    results_5 = {}
    results_6 = {}
    results_7 = {}
    for _ in range(10):
        boards.append(choice(all_boards))

    for b in boards:
        results_5[b] = main("./boards/" + b, 5)
        results_6[b] = main("./boards/" + b, 6)
        results_7[b] = main("./boards/" + b, 7)

    with open('results_5.txt', 'w') as f:
        for key, value in sorted(results_5.items()):
            f.write(key + ': ' + str(value) + '\n')

    with open('results_6.txt', 'w') as f:
        for key, value in sorted(results_6.items()):
            f.write(key + ': ' + str(value) + '\n')

    with open('results_7.txt', 'w') as f:
        for key, value in sorted(results_7.items()):
            f.write(key + ': ' + str(value) + '\n')



if __name__ == "__main__":
    graph()