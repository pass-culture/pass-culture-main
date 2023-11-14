import typing

from pcapi.utils.clean_accents import clean_accents


def sanitize_str(a: typing.Any) -> typing.Any:
    if isinstance(a, str):
        return clean_accents(a.lower())
    return a


def sanitize_list(l: list) -> list:
    return list(map(sanitize_str, l))


def soft_equals(a: object, b: object) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return sanitize_str(str(a)) == sanitize_str(str(b))
    if isinstance(a, bool) and isinstance(b, bool):
        return bool(a) is bool(b)
    return a == b


def less(a: typing.Any, b: typing.Any, *args: typing.Any) -> bool:
    types = set([type(a), type(b)])
    if float in types or int in types:
        try:
            a, b = float(a), float(b)
        except TypeError:
            # NaN
            return False
    return a < b and (not args or less(b, *args))


def less_or_equal(a: typing.Any, b: typing.Any, *args: typing.Any) -> bool:
    return (less(a, b) or soft_equals(a, b)) and (not args or less_or_equal(b, *args))


def contains(a: str, b: list[str]) -> bool:
    """Checks if the list b contains the element a
    1. We check if the element b is a list. If it is not, we raise an exception
    2. We sanitize the element a and b and check if any element in b is in a
    """
    if not a:
        return False
    if not isinstance(b, list):
        raise TypeError(f"{b} is not a list")

    a = sanitize_str(a)
    b = sanitize_list(b)

    return any(element in a for element in b)


def contains_exact(a: str, b: list[str]) -> bool:
    if not a:
        return False
    if not isinstance(b, list):
        raise TypeError(f"{b} is not a list")

    split_a = sanitize_list(a.split())
    b = sanitize_list(b)

    return any(element in split_a for element in b)


OPERATIONS = {
    "==": soft_equals,
    "!=": lambda a, b: not soft_equals(a, b),
    ">": lambda a, b: less(b, a),  # pylint: disable=arguments-out-of-order
    ">=": lambda a, b: less(b, a) or soft_equals(a, b),  # pylint: disable=arguments-out-of-order
    "<": less,
    "<=": less_or_equal,
    "in": lambda a, b: sanitize_str(a) in sanitize_list(b) if "__contains__" in dir(b) else False,
    "not in": lambda a, b: (sanitize_str(a) not in sanitize_list(b)) if "__contains__" in dir(b) else True,
    "contains": contains,
    "contains-exact": contains_exact,
}
