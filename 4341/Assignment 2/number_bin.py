import random
import math


class NumberBin:
    def __init__(self, name, nums):
        self.fitness_probability = None
        self.name = name
        self.bin_list = nums
        self.operators = {1: math.prod, 2: sum, 3: lambda x: max(x) - min(x),
                          4: lambda x: 0}
        self.fitness_function = self.operators[self.name]

    def __repr__(self):
        '''
        Prints the number bin
        :return: string representation of the number bin
        '''
        return f"Bin #{self.name} {self.fitness()} {self.bin_list}"

    def fitness(self):
        '''
        Calculates the fitness of the number bin
        :return: int fitness of the number bin
        '''
        return self.fitness_function(self.bin_list)
