#!/usr/bin/python3.11
import os
from pprint import pprint as print_list
import re as regex


class function:
    def __init__(self, signature, start, end, body, function_calls, file):
        # function signature
        self.signature = f"{signature.split('function')[-1].split('(')[0]}"
        self.start = start  # char index of function start in file
        self.end = end  # char index of function end in file
        self.calls = set(())  # list of functions called by this function
        self.body = body  # string that is the body of the function
        self.function_calls = function_calls
        self.file = file

    def __repr__(self) -> str:
        return f"Function: {self.signature}() start: {self.start} end: {self.end}"


class FileLoader:
    def __init__(self, parent_dir: str, file_ext: str):
        self.dir = parent_dir  # directory to search for files
        self.ext = file_ext  # file extension to search for
        self.files = []  # list of files found

    # find all files in directory with specified extension and add them to self.files

    def load_files(self) -> list[str]:
        for root, dirs, files in os.walk(self.dir):
            for file in files:
                if file.endswith(self.ext):
                    self.files.append(os.path.join(root, file))
        return self.files

    # find all occurences of a string in a string returns a list of indices of the start of the string at each occurence

    def _find_all_orrurences(self, string, pattern) -> list[int]:
        return [m.start() for m in regex.finditer(pattern, string)]

    # count the number of occurences of a character in a list of tuples (int, char)
    def _count_occurence_in_list(self, l: list[tuple[int, str]], item: str) -> int:
        if not l:
            return 0
        count = 0
        for pair in l:
            ignored_value, character = pair
            if character == item:
                count += 1
        return count

    def parse_file_for_functions(self, file: str) -> list[function]:
        functions = []
        # print("FILE: " + file)
        with open(file, "r") as f:
            whole = f.read()
        self.function_definitions = self._find_all_orrurences(
            whole, "[# | *]{0}function (.*)[(]"
        )
        for func, func_start in enumerate(self.function_definitions):

            unclosed_braces = 0
            char_number = func_start
            body = ""
            first_brace = -1

            # this gets us to the first { in case of weird formatting
            try:
                while True:
                    if whole[char_number] == '{':
                        body += '{'
                        unclosed_braces += 1
                        first_brace = char_number
                        char_number += 1
                        break
                    else:
                        char_number += 1
            except IndexError:
                # with open("sus-manager/CFI/static analysis/error.log", "a+") as f:
                #     f.write(
                #         f"Error in file: {file} at function: {whole[func_start:whole[func_start:].index(';')]}\n")
                #     index_of_paren = whole[func_start:].index('(')
                #     print(whole[func_start:index_of_paren])
                continue

            for count, character in enumerate(whole[char_number:]):
                body += character
                if character == "{":
                    unclosed_braces += 1
                elif character == "}":
                    unclosed_braces -= 1
                if unclosed_braces == 0:  # if this is the last closing brace, and therefore the body contains the entire function
                    function_call_regex = "(\w+)\s*[(]"
                    calls = self.remove_non_functions(
                        set(regex.findall(function_call_regex, body)))
                    functions.append(
                        function(
                            whole[func_start:first_brace],
                            first_brace,
                            first_brace + count,  # count is number of chars since the first brace
                            body,
                            calls,
                            file
                        )
                    )
                    break
        return functions

    def get_calls(self, file: str) -> list[function]:
        # find all function calls in a file
        with open(file, "r") as f:
            whole = f.readlines()
        calls = []
        function_call_regex = "(\w+)\s*[(]"
        for count, line in enumerate(whole):
            funcs = self.remove_non_functions(
                set(regex.findall(function_call_regex, line)))
            if funcs:
                for func in funcs:
                    calls.append(f"{func}:{count}")
        return calls

    def remove_non_functions(self, functions: set[function]) -> list[function]:
        if not functions:
            return []
        incorrect_values = {"if", "else", "for",
                            "while", "switch", "case", "default", "define", "defined"}
        for value in incorrect_values:
            functions.discard(value)
        return list(functions)

    def old_parse_file_for_functions(self, file: str) -> list[function]:
        functions = set()
        print("FILE: " + file)
        with open(file, "r") as f:
            whole = f.read()
        self.function_definitions = self._find_all_orrurences(
            whole, "[# | *]{0}function (.*)[(]"
        )
        for func, func_start in enumerate(self.function_definitions):
            braces = []
            for count, character in enumerate(whole[func_start:]):
                if (
                    self._count_occurence_in_list(braces, "{")
                    == self._count_occurence_in_list(braces, "}")
                ) and self._count_occurence_in_list(braces, "{") != 0:
                    functions.append(
                        function(
                            whole[func_start: braces[0][0]],
                            braces[0][0],
                            braces[-1][0],
                            ""  # I added this for testing, this is not part of the old function
                        )
                    )
                    break
                if character == "{" or character == "}":
                    braces.append((count + func_start, character))
        return functions

    def parse_function_for_calls(self, function: function) -> function:
        # regex to find function calls
        function.calls = self._find_all_orrurences(
            function.signature, "([a-zA-Z0-9_]+)[(]"
        )
        return function


if __name__ == "__main__":
    file_loader = FileLoader(
        "/home/student/sus-stuff/mqp_sus_history/sus-manager/wp-versions/wp-511-ubuntu/nginx-fpm-build/wordpress",
        ".php",
    )
    file_loader.load_files()


with open("functions-line-num.txt", "w") as f:
    for file in file_loader.files:
        functions = file_loader.get_calls(file)
        f.write(f"{file.split('nginx-fpm-build/wordpress/')[-1]}: ")
        for function in functions:
            funcs, line = function.split(":")
            f.write(f"{funcs}|{line} ")
        f.write("\n")

    # all_functions = {}

    # for f in file_loader.files:
    #     list_of_functions = file_loader.parse_file_for_functions(f)
    #     # print_list(list_of_files)
    #     for f in list_of_functions:
    #         all_functions[f.file] = f.function_calls

    #     # break  # THIS IS TEMPORARY FOR TESTING

    # print("DICTIONARY OF FOUND FUNCTIONS:")
    # with open("CFI/static analysis/functions.txt", "w+") as f:
    #     for k, v in all_functions.items():
    #         calls = ""
    #         for call in v:
    #             calls += call + " "
    #         to_write = f"{k.strip().split('nginx-fpm-build/wordpress/')[-1]}: {calls.strip()} \n"
    #         print(to_write)
    #         f.write(to_write)
