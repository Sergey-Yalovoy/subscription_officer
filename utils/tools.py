from functools import reduce


def change_case(input_string: str) -> str:
    return reduce(
        lambda x, y: x + ("_" if y.isupper() else "") + y, input_string
    ).lower()
