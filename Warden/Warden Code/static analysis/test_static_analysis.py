#!/usr/bin/python3.11
from fileinput import close
import re
#php function to sort by length of string.

class function:
    def __init__(self, name, start, end):
        self.name = name #don't know how to get the name yet
        self.start = start
        self.end = end
    
    def __repr__(self) -> str:
        return f"Function: {self.name} start: {self.start} end: {self.end}"


program = '''function count_to_one_million() { 
    for ($i = 0; $i < 1000000; $i++) { 
        echo $i; 
    }
}

function count_to_two_million() { 
    for ($i = 0; $i < 2000000; $i++) { 
        echo $i; 
    }
}

function count_to_three_million() { 
    for ($i = 0; $i < 3000000; $i++) { 
        echo $i; 
    }
}
'''

def _find_all_orrurences(string, pattern):
    return [m.start() for m in re.finditer(pattern, string)]
function_definitions = _find_all_orrurences(program, "function")
print(f"functions begin at {function_definitions}")

def _count_occurence_in_list(l: list, item: str) -> int:
    if not l:
        return 0
    count = 0
    for pair in l:
        trash, character = pair
        if character == item:
            count += 1
    return count

functions = []
for func,func_start in enumerate(function_definitions):
    braces = []
    for count,character in enumerate(program[func_start:]):
        if _count_occurence_in_list(braces, "{") == _count_occurence_in_list(braces, "}") and _count_occurence_in_list(braces, "{") != 0:
                functions.append(function(program[func_start:braces[0][0]],braces[0][0],braces[-1][0]))
                break
        if character == "{" or character == "}":
            braces.append((count+func_start, character))


for func in functions:
    print(func)
