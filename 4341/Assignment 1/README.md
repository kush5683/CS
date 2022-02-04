# Assignment 1 for 4341 Artificial Intelligence
----
# See assignment 1 instructions for details.

# Usage
----
## To run the program, type the following in the terminal:
```angular2html
python3 astar.py <input_file> <heuristic>
```
## The input file should be a text file that is tab seperated. With S denoting the start position and G denoting the goal position.
Sample board:
```angular2html
4	G	4	6
2	9	9	6
1	4	S	3
```

## The heuristic should be a whole number between 1 and 6 inclusive. 
| Heuristic number  | Heuristic Function                                       |
|-------------------|----------------------------------------------------------| 
| 1                 | 0                                                        |
| 2                 | min(vertical, horizontal)                                |
| 3                 | max(vertical, horizontal)                                |
| 4                 | vertical + horizontal                                    |
| 5                 | (vertical + horizontal) - 1 + min(start_neighbors)       |
| 6                 | ((vertical + horizontal) - 1 + min(start_neighbors)) * 3 |

