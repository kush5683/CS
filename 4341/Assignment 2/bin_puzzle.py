import math
from ga_functions import selection, elitism, culling
from number_bin import NumberBin
from bin_collection import BinCollection
from random import random, shuffle, choice
import time as timer


def bin_puzzle(filename, time, when_to_introduce_culling=1000, mutation_threshold=0.01):
    """
    main function for bin puzzle
    """
    ELITE = True
    CULLING = True
    generations = 0
    population = []
    population_size = 100
    nums = None  # initialize nums
    with open(filename, 'r') as f:
        nums = [float(num.replace("\n", "")) for num in
                f.readlines()]  # read all numbers from file and convert to float
    # print(nums)  # print numbers

    # assign numbers to bins
    for i in range(population_size):
        shuffle(nums)  # shuffle numbers
        # print(nums)  # print shuffled numbers
        bin_one = NumberBin(name=1, nums=nums[:10])  # bin one, first 10 numbers, multiplication
        bin_two = NumberBin(name=2, nums=nums[10:20])  # bin two, second 10 numbers, addition
        bin_three = NumberBin(name=3, nums=nums[20:30])  # bin three, third 10 numbers, difference
        bin_four = NumberBin(name=4, nums=nums[30:40])  # bin four, fourth 10 numbers, dummy

        collection = BinCollection(bin_one, bin_two, bin_three, bin_four, nums)  # create collection of bins
        population.append(collection)  # add collection to population
    # add bins to population

    # start timer
    end = timer.time() + time
    start = timer.time()
    new_population = []
    top_ever = float('-inf')
    top_solution = ""
    best_generation = 0
    """
    
    Run for the specified time
    
    """
    print(f"RUNNING FOR {time} SECONDS")
    while timer.time() < end:
        """
        
        Save/ check for best 
        
        """
        for o in population:
            o.validate()
        if max(population).fitness() >= top_ever:
            top_ever = max(population).fitness()
            top_solution = str(max(population))
            best_generation = generations
        if generations % 100 == 0:
            print(f"Generation {'{:,}'.format(generations)}\t time: {'{:,}'.format(float('{:.1f}'.format(timer.time() - start)))}\t "
                  f"best: {'{:,}'.format(float('{:.3f}'.format(top_ever)))}")
        """
        
        Save best with elitism and remove worst with culling
        
        """
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
    temp = f"Generation {'{:,}'.format(generations)}\t time: {'{:,}'.format(float('{:.1f}'.format(timer.time() - start)))}\t best: {'{:,}'.format(float('{:.3f}'.format(top_ever)))}"
    print(f"{'-' * (len(temp) + 5)}")
    print(f"Ran for {'{:.2f}'.format(timer.time() - start)} seconds")
    print(f"Score: {'{:,}'.format(float('{:.3f}'.format(top_ever)))}")
    print(f"Ran for {'{:,}'.format(generations)} generations")
    print(f"Best generation: {'{:,}'.format(best_generation)}")
    print(top_solution)
    return top_ever, best_generation, generations


if __name__ == "__main__":
    bin_puzzle("numbers.txt", 60)
