from main import main as run_astar
import os
from board import Board
from node import Node
from gen_board import validate
from math import ceil, sqrt
import time as timer
import csv


def setup_csv():
    with open('trainer_agent.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["Manhattan Distance", "Straightline Distance", "True Path Length"])  # write headers


def write_features_to_csv(rows):
    """
    Write the features to a csv file
    :return:
    """
    with open('trainer_agent.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            writer.writerow(row)


class TrainerAgent:
    def __init__(self, current_position, current_direction, goal_location, true_cost):
        self.current_position = current_position
        self.current_direction = current_direction
        self.goal_location = goal_location
        self.true_cost = true_cost
        self.features = []

    def calculate_features(self):
        """
        Calculate the value per feature and store it in a list to write to csv
        :return:
        """
        self.features.append(self.calculate_manhattan_distance())
        self.features.append(self.calculate_straightline_distance())
        # self.features.append(self.calculate_facing_goal())
        self.features.append(self.true_cost)
        return self.features

    def calculate_manhattan_distance(self):
        """
        Calculate the manhattan distance between the current position and the goal location
        :return:
        """
        diff_r = abs(self.current_position[0] - self.goal_location[0])
        diff_c = abs(self.current_position[1] - self.goal_location[1])
        return diff_r + diff_c

    def calculate_straightline_distance(self):
        diff_r = abs(self.current_position[0] - self.goal_location[0]) ** 2
        diff_c = abs(self.current_position[1] - self.goal_location[1]) ** 2

        return sqrt(diff_r + diff_c)

    def calculate_facing_goal(self):
        if self.current_direction == 'north' and self.goal_location[0] > self.current_position[0]:
            return 1
        elif self.current_direction == 'south' and self.goal_location[0] < self.current_position[0]:
            return 1
        elif self.current_direction == 'east' and self.goal_location[1] > self.current_position[1]:
            return 1
        elif self.current_direction == 'west' and self.goal_location[1] < self.current_position[1]:
            return 1
        else:
            return 0


if __name__ == '__main__':
    setup_csv()
    boards = os.listdir('./boards')
    for count, b in enumerate(boards):
        if not validate("./boards/" + b):
            continue
        end = timer.time() + 15
        start = timer.time()
        while timer.time() < end:
            results = run_astar("./boards/" + b, 5)
            score = results[0]
            len_of_path = results[1]
            nodes_expanded = results[2]
            actions_taken = results[3]
            path = results[4]
            board = results[5]
            true_astar_cost = [0]
            temp_data = [[0, 0.0, 0]]
            for action, node in zip(actions_taken, path):
                if action == "START":
                    break
                actions = {"FORWARD": abs(board.get_cost(node.row, node.col)),
                           "LEFT": ceil(board.get_cost(node.row, node.col) / 2),
                           "RIGHT": ceil(board.get_cost(node.row, node.col) / 2), "BASH": 3}
                true_astar_cost.append(actions[action] + true_astar_cost[-1])
                trainer = TrainerAgent([node.row, node.col], node.direction, board.get_goal(),
                                       true_astar_cost[-1])
                temp_data.append(trainer.calculate_features())
            temp_data.reverse()
            print(f"RAN {count+1}/{len(boards)} and took {timer.time() - start} seconds")
            write_features_to_csv(temp_data)
            break
