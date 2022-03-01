from io import StringIO

from bin_puzzle import bin_puzzle
import os
import sys
import pandas as pd

import matplotlib.pyplot as plt


def run_tests(filename):

    gens = []
    fitnesses = []
    excel = pd.read_excel(filename)
    excel.to_csv('data.csv', index=False, header=True)
    df = pd.DataFrame(pd.read_csv('data.csv'))
    for count,m in enumerate(df.Mean):
        gens.append(count*100)
        fitnesses.append(m)
    fig = plt.figure()
    plt.plot(gens, fitnesses)
    plt.xlabel("generation")
    plt.ylabel("Fitness")
    plt.title(f"Average Fitness Score vs generation")
    plt.suptitle("Elitism and Culling Disabled [Castle Puzzle]")
    plt.show()


if __name__ == '__main__':
    run_tests("formatted_data_castle_no_elite_no_cull.xlsx")
