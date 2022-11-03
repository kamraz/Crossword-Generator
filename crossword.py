from collections import Counter
import random
import yaml
import sys
import os


def load_word_list(filename):
    "load a list of words and scores from a file"
    word_list = []
    for line in open(filename):
        word, score = line.strip().split(";")
        word_list.append([word, int(score)])
    return word_list


def initialize_crossword(width: int, height: int, stops: list[tuple[int, int]]):
    grid = [[None for i in range(width)] for j in range(height)]
    for row, col in stops:
        grid[row][col] = "#"
    word_slots = find_word_slots(grid, width, height)
    empty_word_slots = word_slots.copy()
    return Crossword(grid, word_slots, empty_word_slots, [])


# TODO: add to solver function
def find_word_slots(grid: list[list[str]], width: int, height: int):
    "finds all the word slots in the crossword puzzle"
    word_slots = {}
    for i in range(height):
        for j in range(width):
            if grid[i][j] is None:
                if j == 0 or grid[i][j - 1] == "#":
                    length = count_space(grid, i, j, "across")
                    if length > 1:
                        word_slots[(i, j, "across")] = length
                if i == 0 or grid[i - 1][j] == "#":
                    length = count_space(grid, i, j, "down")
                    if length > 1:
                        word_slots[(i, j, "down")] = length
    return word_slots


# TODO: add to solver function
def count_space(grid, row, col, direction):
    "count the number of space in a word slot"
    if direction == "across":
        count = 0
        while col < len(grid[0]) and grid[row][col] is None:
            count += 1
            col += 1
        return count
    elif direction == "down":
        count = 0
        while row < len(grid) and grid[row][col] is None:
            count += 1
            row += 1
        return count


class Crossword:
    "representation of a crossword puzzle for creating crossword puzzles"

    def __init__(
        self,
        grid: list[list[str]],
        word_slots: dict[tuple[int, int, str], int],
        empty_word_slots: dict[tuple[int, int, str], int],
        words: list[tuple[str, int, int, str]],
    ):
        self.grid = grid
        self.word_slots = word_slots
        self.empty_word_slots = empty_word_slots
        self.words = words
        self.height = len(grid)
        self.width = len(grid[0])

    def __str__(self):
        "returns a string representation of the crossword puzzle"
        result = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] is not None:
                    result += self.grid[i][j]
                elif (i, j, "across") in self.word_slots and (
                    i,
                    j,
                    "down",
                ) in self.word_slots:
                    result += "↘"
                elif (i, j, "across") in self.word_slots:
                    result += "→"
                elif (i, j, "down") in self.word_slots:
                    result += "↓"
                else:
                    result += "-"
            result += "\n"
        return result

    def copy(self):
        "returns a copy of the crossword puzzle"
        return Crossword(
            self.grid[:],
            self.word_slots.copy(),
            self.empty_word_slots.copy(),
            self.words[:],
        )

    def print_final(self):
        "prints the final crossword puzzle"
        result = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] is not None:
                    result += self.grid[i][j]
                else:
                    result += "#"
            result += "\n"
        print(result)
        # print the words nicely formatted
        words_list = []
        for word, _, _, _ in self.words:
            words_list.append(word)
        words_list.sort(key=lambda x: len(x), reverse=True)
        print(", ".join(words_list))

    def final_str(self):
        result = ""
        for i in range(self.height):
            for j in range(self.width):
                if self.grid[i][j] is not None:
                    result += self.grid[i][j]
                else:
                    result += "#"
            result += "\n"
        # print the words nicely formatted
        words_list = []
        for word, _, _, _ in self.words:
            words_list.append(word)
        words_list.sort(key=lambda x: len(x), reverse=True)
        word_str = ", ".join(words_list)
        return result, word_str

    # Should be called with the word dictionary as a parameter
    def place_word(
        self, word: str, row: int, col: int, direction: str, word_dict_by_length
    ):
        "places a word in the crossword puzzle"
        if (row, col, direction) not in self.empty_word_slots:
            print(self)
            print(word)
            print(f"({row}, {col}, {direction})")
            raise ValueError("word slot does not exist")
        # deep copy nested array
        temp_grid = [row[:] for row in self.grid]
        if direction == "across":
            for i in range(len(word)):
                if (
                    self.grid[row][col + i] is not None
                    and self.grid[row][col + i] != word[i]
                ):
                    return False
                temp_grid[row][col + i] = word[i]
        elif direction == "down":
            for i in range(len(word)):
                if (
                    self.grid[row + i][col] is not None
                    and self.grid[row + i][col] != word[i]
                ):
                    return False
                temp_grid[row + i][col] = word[i]

        # Loop through every unused slot, make sure it creates a legal word
        # If not return a failure
        # Add newly created words to the wordlist and remove them from the empty word slots
        new_words = []
        for slot, i_length in self.empty_word_slots.items():
            i_row, i_col, i_direction = slot
            chars = self.get_chars_at(temp_grid, i_row, i_col, i_direction, i_length)
            if None in chars:
                continue
            i_word = "".join(chars)
            if i_word not in word_dict_by_length[i_length]:
                # print(
                #     f"fail: {word} at ({row}, {col}, {direction}, {i_word} at ({i_row}, {i_col}, {i_direction})"
                # )
                return False
            new_words.append((i_word, i_row, i_col, i_direction))

        new_empty_word_slots = self.empty_word_slots.copy()
        new_word_slots = self.word_slots.copy()
        for new_word, new_row, new_col, new_direction in new_words:
            new_empty_word_slots.pop((new_row, new_col, new_direction))
        new_words = self.words + new_words
        return Crossword(temp_grid, new_word_slots, new_empty_word_slots, new_words)

    def clear_word(self, word: str, row: int, col: int, direction: str):
        "clears a word from the crossword puzzle"
        if (row, col, direction) not in self.word_slots:
            raise ValueError("word slot does not exist")
        if (word, row, col, direction) not in self.words:
            raise ValueError("word does not exist")
        if direction == "across":
            for i in range(len(word)):
                self.grid[row][col + i] = None
        elif direction == "down":
            for i in range(len(word)):
                self.grid[row + i][col] = None
        self.words.remove((word, row, col, direction))
        self.empty_word_slots[(row, col, direction)] = len(word)

    # # Abstract to solver class
    # def brute_force_add_words(self, word_dict_by_length):
    #     "brute force add words to the crossword puzzle"
    #     for word_slot in list(self.empty_word_slots):
    #         if word_slot not in self.empty_word_slots:
    #             continue
    #         row, col, direction = word_slot
    #         length = self.empty_word_slots[word_slot]
    #         for word in word_dict_by_length[length]:
    #             if self.place_word(word, row, col, direction, word_dict_by_length):
    #                 break
    #     if len(self.empty_word_slots.keys()) > 0:
    #         print(f"INVALID PUZZLE Unfilled Slots: {self.empty_word_slots}")
    #         print(self)
    #         return False
    #     else:
    #         print("PUZZLE SOLVED")
    #         print(self.print_final())
    #         return True

    def get_chars_at(self, grid, row, col, direction, length):
        "get the characters at a given location"
        if direction == "across":
            return grid[row][col : col + length]
        elif direction == "down":
            return [grid[row + i][col] for i in range(length)]

    def print_word_slot_length_frequency(self):
        "print the frequency of word slot lengths"
        slot_sizes = self.get_slot_sizes()
        totals = Counter(slot_sizes)
        totals_str = ""
        for key in sorted(list(totals.keys())):
            totals_str += f"{key}: {totals[key]}, "
        print(totals_str[:-2])


class Crossword_Solver:
    "Class for solving a crossword puzzle"
    # TODO: Set hyperparameters for wordlist heuritic candidate genration
    # TODO: Add verbosity param
    # TODO: Add a stop condition for a certain # of valid solitions
    def __init__(self, word_list: list[list[str, int]], custom_words: list[str]):
        self.custom_words = custom_words
        for word in self.custom_words:
            word_list.append([word.upper(), 100])
        self.word_list = word_list
        self.word_dict_by_length: dict[int, list[str, int]] = {}
        # make a dict instead of list for faster lookup
        for word, score in self.word_list:
            if len(word) not in self.word_dict_by_length:
                self.word_dict_by_length[len(word)] = []
            # remove useless words as suggested by list curator
            if score > 40:
                self.word_dict_by_length[len(word)].append([word, score])

        for length in self.word_dict_by_length:
            self.word_dict_by_length[length].sort(key=lambda x: x[1], reverse=True)
            self.word_dict_by_length[length] = list(
                map(lambda x: x[0], self.word_dict_by_length[length])
            )

    def create_base_crossword(
        self,
        board_shape: tuple[int, int],
        words: list[tuple[str, int, int, str]],
        blocks: list[int, int],
    ):
        "create a crossword puzzle with the given words and blocks"
        height, width = board_shape
        grid = [[None for i in range(width)] for j in range(height)]
        for row, col in blocks:
            grid[row][col] = "#"
        word_slots = find_word_slots(grid, width, height)
        empty_word_slots = word_slots.copy()
        crossword = Crossword(grid, word_slots, empty_word_slots, [])
        for word, row, col, direction in words:
            crossword = crossword.place_word(
                word.upper(), row, col, direction, self.word_dict_by_length
            )
            if crossword is False:
                raise ValueError(
                    f"Word: {word} is placed in an invalid location, or is not in the word list"
                )
        return crossword

    def solve(self, crossword: Crossword):
        solutions = self.huristic_bfs_solve(crossword)
        if len(solutions) == 0:
            print("PUZZLE UNSOLVABLE WITH CURRENT HYPERPARAMETERS")
        else:
            # Loop over all solutions, save them to text file
            text = []
            for cross in solutions:
                cross, words = cross.final_str()
                text.append(cross)
                text.append(words)
                text.append("-" * 20)
            with open("solutions.txt", "w") as f:
                f.write("\n".join(text))

    def bfs_solve(self, crossword):
        "solve the crossword puzzle using breadth first search"
        queue = [crossword]
        while len(queue) > 0:
            current_crossword = queue.pop(0)
            if len(current_crossword.empty_word_slots) == 0:
                print("PUZZLE SOLVED")
                print(current_crossword.print_final())
                return True
            for word_slot in list(current_crossword.empty_word_slots):
                if word_slot not in current_crossword.empty_word_slots:
                    continue
                row, col, direction = word_slot
                length = current_crossword.empty_word_slots[word_slot]
                i = 0
                for word in self.word_dict_by_length[length]:
                    new_cross = crossword.place_word(
                        word, row, col, direction, self.word_dict_by_length
                    )
                    if new_cross:
                        print(new_cross)
                        queue.append(new_cross)
                    i += 1
                    if i > 3:
                        break
        print("PUZZLE UNSOLVABLE")
        return False

    # Return list of complete crosswords
    def huristic_bfs_solve(self, crossword):
        "solve the crossword puzzle using breadth first search"
        queue = [crossword]
        a = 0
        print("-" * 20)
        solutions = []
        while len(queue) > 0:
            current_crossword = queue.pop(0)
            if len(current_crossword.empty_word_slots) == 0:
                print("PUZZLE SOLVED")
                solutions.append(current_crossword)
            else:
                word_slot = max(
                    current_crossword.empty_word_slots,
                    key=current_crossword.empty_word_slots.get,
                )
                print(word_slot)
                row, col, direction = word_slot
                length = current_crossword.empty_word_slots[word_slot]
                i = 0
                for word in self.word_dict_by_length[length]:
                    new_cross = current_crossword.place_word(
                        word, row, col, direction, self.word_dict_by_length
                    )
                    if new_cross:
                        print(new_cross)
                        queue.append(new_cross)
                        i += 1
                        if i > 4:
                            break
        return solutions

    def recursive_solve(self, crossword: Crossword):
        "recursive solver"
        if len(crossword.empty_word_slots.keys()) == 0:
            print("PUZZLE SOLVED")
            print(crossword.print_final())
            return True
        # Get the wordslot with the largest value
        word_slot = max(crossword.empty_word_slots, key=crossword.empty_word_slots.get)
        if word_slot not in crossword.empty_word_slots.keys():
            self.recursive_solve(crossword.copy())

        row, col, direction = word_slot
        length = crossword.empty_word_slots[word_slot]
        tries = 0
        for word in self.word_dict_by_length[length]:
            new_cross = crossword.place_word(
                word, row, col, direction, self.word_dict_by_length
            )
            if new_cross:
                print(new_cross)
                if self.recursive_solve(new_cross):
                    return True
            tries += 1
            # After trying x words give up on this branch
            if tries > 50000:
                return False
        print("backtracking")
        return False

def main():
    # Check if config file is provided as command line argument
    config_file = "puzzle_config.yaml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    # Check if config file exists
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        print("Please create a puzzle_config.yaml file or provide a valid path.")
        sys.exit(1)
    
    # Load configuration from YAML file
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    
    # Extract configuration values
    word_list_file = config.get('word_list_file', 'peter-broda-wordlist__scored.txt')
    custom_words = config.get('custom_words', [])
    words = config.get('words', [])
    board_shape = tuple(config.get('board_shape', [8, 8]))
    necessary_blockers = config.get('necessary_blockers', [])
    optional_blockers = config.get('optional_blockers', [])
    
    # Create solver
    solver = Crossword_Solver(
        word_list=load_word_list(word_list_file),
        custom_words=custom_words,
    )
    
    # Create crossword
    crossword = solver.create_base_crossword(
        board_shape,
        words,
        necessary_blockers + optional_blockers,
    )
    solver.solve(crossword)


if __name__ == "__main__":
    main()
