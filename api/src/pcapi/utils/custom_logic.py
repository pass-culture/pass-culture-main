from pcapi.utils.clean_accents import clean_accents


def sanitize_str(a: object) -> object:
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


def less(a: object, b: object, *args) -> bool:  # type: ignore [no-untyped-def]
    types = set([type(a), type(b)])
    if float in types or int in types:
        try:
            a, b = float(a), float(b)  # type: ignore [arg-type]
        except TypeError:
            # NaN
            return False
    return a < b and (not args or less(b, *args))  # type: ignore [operator]


def less_or_equal(a: object, b: object, *args) -> bool:  # type: ignore [no-untyped-def]
    return (less(a, b) or soft_equals(a, b)) and (not args or less_or_equal(b, *args))


def contains(a, b) -> bool:  # type: ignore [no-untyped-def]
    """Checks if the list b contains the element a"""
    if not a:
        return False
    if not isinstance(b, list):
        raise TypeError(f"{b} is not a list")
    return (
        any(sanitize_str(element) in sanitize_str(a) for element in b)  # type: ignore [operator]
        if "__contains__" in dir(b)
        else sanitize_str(b) in sanitize_str(a)  # type: ignore [operator]
    )


def contains_exact(a, b) -> bool:  # type: ignore [no-untyped-def]
    if not a:
        return False
    return (
        any(sanitize_str(element) in sanitize_list(a.split()) for element in b)
        if "__contains__" in dir(b)
        else sanitize_str(b) in sanitize_str(a)  # type: ignore [operator]
    )


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
