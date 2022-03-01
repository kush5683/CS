from castle import Castle
from castle_piece import Piece
from random import random, randint, shuffle, choice
from ga_functions import selection, elitism, culling
import time as timer


def castle_puzzle(filename, time, when_to_introduce_culling=90, mutation_threshold=0.1):
    ELITE = True
    CULLING = True
    generations = 0
    population = []
    population_size = 100
    pieces = []
    with open(filename, 'r') as f:
        temp = f.readlines()
        for line in temp:
            p = [pi.strip().replace("\n", "") for pi in line.split("\t")]
            pieces.append(Piece(p[0], int(p[1]), int(p[2]), int(p[3])))

    for i in range(population_size):
        shuffle(pieces)
        height = randint(3, len(pieces))
        temp = [choice(pieces) for i in range(height)]
        population.append(Castle(temp, pieces))
    # print(population)

    end = timer.time() + time
    start = timer.time()
    new_population = []
    top_of_population = float('-inf')
    top_solution = ""
    best_generation = 0
    while timer.time() < end:

        for o in population:
            o.validate()
        if max(population).fitness() >= top_of_population:
            top_of_population = max(population).fitness()
            top_solution = str(max(population))
            best_generation = generations
        if generations % 100 == 0:
            print(
                f"Generation {'{:,}'.format(generations)}\t time: {'{:,}'.format(float('{:.1f}'.format(timer.time() - start)))}\t "
                f"best: {'{:,}'.format(float('{:.3f}'.format(top_of_population)))}")

        # get the organisms that will be saved with elitism
        if ELITE:
            elite = elitism(population)
            for e in elite:
                new_population.append(e)
        # get the organisms that will be removed with culling
        if CULLING:
            culled = culling(population)
            # start culling process at given generation
            if generations >= when_to_introduce_culling:
                for c in culled:
                    population.remove(c)

        """
        Fill the population
        """
        pairs = []
        while len(new_population) < population_size:

            # select parents
            select_from = selection(population)
            parent_A = choice(select_from)
            parent_B = choice(select_from)
            # ensure parents are different, and they have not been paired before
            while parent_A == parent_B or (parent_A, parent_B) in pairs:
                parent_B = choice(population)
            pairs.append((parent_A, parent_B))
            # create children and add them to the new population
            children = parent_A.crossover(parent_B)
            new_population.append(children[0])
            new_population.append(children[1])
        # mutate the new population
        for c in new_population:
            chance = random()
            if chance < mutation_threshold:
                c.mutate()
        generations += 1
    population = new_population.copy()  # replace population with new population
    new_population = []  # reset new population
    temp = f"Generation {'{:,}'.format(generations)}\t time: {'{:,}'.format(float('{:.1f}'.format(timer.time() - start)))}\t best: {'{:,}'.format(float('{:.3f}'.format(top_of_population)))}"
    print(f"{'-' * (len(temp) + 5)}")
    print(f"Ran for {'{:.2f}'.format(timer.time() - start)} seconds")
    print(f"Score: {'{:,}'.format(float('{:.3f}'.format(top_of_population)))}")
    print(f"Ran for {'{:,}'.format(generations)} generations")
    print(f"Best generation: {'{:,}'.format(best_generation)}")
    print(top_solution)
    return top_of_population, best_generation, generations


if __name__ == '__main__':
    castle_puzzle('castle.txt', 1)

"""
python ga.py 2 castle.txt 1 | tee castle_puzzle_run_1.txt;python ga.py 2 castle.txt 1 | tee castle_puzzle_run_2.txt;python ga.py 2 castle.txt 1 | tee castle_puzzle_run_3.txt;python ga.py 2 castle.txt 1 | tee castle_puzzle_run_4.txt;python ga.py 2 castle.txt 1 | tee castle_puzzle_run_1.txt 

"""