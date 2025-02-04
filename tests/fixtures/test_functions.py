from typing import List, Dict, Set, Any
import random
from datetime import datetime
from .other_functions import multiply, sum_numbers


# .# Pure functions that only use builtins
def sum_two_numbers(x: int, y: int) -> int:
    return x + y


def calculate_text_length(s: str) -> int:
    return len(s)


def create_reversed_sequence(lst: List) -> List:
    return lst[::-1]


def count_aeiou(s: str) -> int:
    return sum(1 for c in s.lower() if c in "aeiou")


# .# Pure functions that call other pure functions
def arithmetic_chain(x: int, y: int, z: int) -> int:
    product = calculate_product(x, y)
    return sum_two_numbers(product, z)


def calculate_product(x: int, y: int) -> int:
    return x * y


def analyze_text(s: str) -> tuple:
    length = calculate_text_length(s)
    vowels = count_aeiou(s)
    return length, vowels


# .# Impure functions using only builtins
def generate_dice_roll() -> int:
    return random.randint(1, 100)


def get_timestamp() -> str:
    return datetime.now().isoformat()


def update_sequence(lst: List, item: Any) -> List:
    lst.append(item)
    return lst


# Global state variables
COUNTER = 0
MEMORY_STORE: Dict[str, int] = {}


# .# Impure functions that call pure functions
def remember_text_length(s: str) -> int:
    if s in MEMORY_STORE:
        return MEMORY_STORE[s]
    result = calculate_text_length(s)
    MEMORY_STORE[s] = result
    return result


def update_counter_with_sum(x: int) -> int:
    global COUNTER
    COUNTER = sum_two_numbers(COUNTER, x)
    return COUNTER


# .# Impure functions that call other impure functions
def collect_metrics(s: str) -> tuple:
    time = get_timestamp()
    length = remember_text_length(s)
    dice = generate_dice_roll()
    return time, length, dice


# .# Functions that look impure but are pure
def create_extended_sequence(lst: List, item: Any) -> List:
    new_list = lst.copy()
    new_list.append(item)
    return new_list


def generate_seeded_number(x: int) -> int:
    # Creates a deterministic "random" number based on input
    random.seed(x)
    result = random.randint(1, 100)
    return result


# .# Functions that look pure but are impure
def double_and_track(x: int) -> int:
    # Doubles a number and updates tracking
    global COUNTER
    COUNTER += 1
    return x * 2


def log_arithmetic(x: int, y: int) -> int:
    # Performs addition and records the operation
    result = sum_two_numbers(x, y)
    with open("log.txt", "a") as f:
        f.write(f"{x} + {y} = {result}\n")
    return result


# .# Pure functions with complex logic
def calculate_nth_sequence_number(n: int) -> int:
    if n <= 1:
        return n
    return calculate_nth_sequence_number(n - 1) + calculate_nth_sequence_number(n - 2)


def extract_unique_elements(lst: List) -> Set:
    return set(lst)


# .# Function that's pure or impure depending on its input
def transform_data(data: Dict, mode: str = "copy") -> Dict:
    if mode == "copy":
        return {k: v * 2 for k, v in data.items()}
    else:
        # Modifies the input dictionary directly
        for k in data:
            data[k] *= 2
        return data


# Modifies the input list by squaring all elements
def square_numbers_inplace(numbers: List[int]) -> List[int]:
    for i in range(len(numbers)):
        numbers[i] = numbers[i] * numbers[i]
    return numbers


# .# Functions that call outside functions
def arithmetic_chain_2(x: int, y: int, z: int) -> int:
    product = multiply(x, y)
    return sum_numbers(product, z)
