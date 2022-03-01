from number_bin import NumberBin
from random import randint


class BinCollection:
    def __init__(self, bin_one, bin_two, bin_three, bin_four, all_numbers):
        self.selection_probability = None
        self.bin_one = bin_one
        self.bin_two = bin_two
        self.bin_three = bin_three
        self.bin_four = bin_four
        self.all_numbers = all_numbers
        self.bins = {1: self.bin_one, 2: self.bin_two, 3: self.bin_three, 4: self.bin_four}
        self.validate()

    def __repr__(self):
        """
        Returns a string representation of the BinCollection object.
        :return:
        """
        return f"Bin 1: {self.bin_one.bin_list}\n" \
               f"Bin 2: {self.bin_two.bin_list}\n" \
               f"Bin 3: {self.bin_three.bin_list}\n" \
               f"Bin 4: {self.bin_four.bin_list}\n" \
               f"--------------------------\n" \
               f"Score: {'{:,}'.format(self.fitness())}"

    def __gt__(self, other):
        return self.fitness() > other.fitness()

    def validate(self):
        """
        Validates that the BinCollection object is valid, i.e. all numbers are only used once
        :return:
        """
        nums = self.all_numbers.copy()
        for b in [self.bin_one, self.bin_two, self.bin_three, self.bin_four]:
            for val in b.bin_list:
                try:
                    nums.remove(val)
                except ValueError:
                    index_to_mutate = b.bin_list.index(val)
                    random_index = randint(0, len(nums) - 1)
                    b.bin_list[index_to_mutate] = nums.pop(random_index)

    def fitness(self):
        """
        Returns the fitness of the BinCollection object.
        :return:
        """
        return sum([self.bin_one.fitness(), self.bin_two.fitness(), self.bin_three.fitness(), self.bin_four.fitness()])

    def mutate(self):
        """
        Mutates the BinCollection object by randomly swapping two values in random bin pair.
        :return:
        """
        bin_A = self.bins.get(randint(1, 4))
        bin_B = self.bins.get(randint(1, 4))
        while bin_A is bin_B:
            bin_B = self.bins.get(randint(1, 4))
        random_index = randint(0, len(bin_A.bin_list) - 1)
        bin_A.bin_list[random_index], bin_B.bin_list[random_index] = \
            bin_B.bin_list[random_index], bin_A.bin_list[random_index]
        self.validate()

    def set_selection_probability(self, selection_probability):
        """
        Set selection probability for BinCollection object.
        :param selection_probability: between 0.0 and 1.0
        :return:
        """
        self.selection_probability = selection_probability

    def crossover(self, other):
        """
        Crossover two BinCollection objects.
        :param other: other BinCollection object
        :return: tuple of children BinCollection objects
        """

        child_one = BinCollection(self.bin_one, self.bin_two,
                                  other.bin_three, other.bin_four, self.all_numbers)
        child_two = BinCollection(other.bin_one, other.bin_two,
                                  self.bin_three, self.bin_four, self.all_numbers)
        return child_one, child_two


