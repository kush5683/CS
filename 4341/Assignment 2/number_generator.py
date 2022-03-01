from random import randint,random


def generate_numbers(n=40):
    """
    Generates a list of numbers from 1 to n.
    """
    nums = []
    for i in range(1, n + 1):
        base = randint(-10, 9)
        mod = random()
        nums.append(float("{:.2f}".format(base + mod)))
    with open("numbers.txt", "w") as f:
        for num in nums:
            print(num)
            f.write(str(num) + "\n")

if __name__ == '__main__':
    generate_numbers()
