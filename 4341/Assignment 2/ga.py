import sys
from bin_puzzle import bin_puzzle
from castle_puzzle import castle_puzzle


def main():
    """
    Main function.
    :param: puzzle number. 1 for bins puzzle, 2 for castle puzzle.
    :param: input file name. txt file for puzzle input.
    :param: run time. number of seconds to run the program.
    :return:
    """
    if len(sys.argv) != 4:
        print("Usage: python3 ga.py <puzzle number (1 or 2)> <input_file.txt> <run time in seconds>")
        raise SystemExit
    puzzle_number = sys.argv[1]  # 1
    input_file = sys.argv[2]  # sample_numbers.txt
    run_time = sys.argv[3]  # 60
    if puzzle_number == "1":
        bin_puzzle(input_file, int(run_time))
    elif puzzle_number == "2":
        castle_puzzle(input_file, int(run_time))


if __name__ == "__main__":
    main()
