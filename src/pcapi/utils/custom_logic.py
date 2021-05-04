# pylint: disable=no-value-for-parameter,arguments-out-of-order
def soft_equals(a: object, b: object) -> bool:
    if isinstance(a, str) or isinstance(b, str):
        return str(a) == str(b)
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) is bool(b)
    return a == b


def less(a: object, b: object, *args) -> bool:
    types = set([type(a), type(b)])
    if float in types or int in types:
        try:
            a, b = float(a), float(b)
        except TypeError:
            # NaN
            return False
    return a < b and (not args or less(b, *args))


def less_or_equal(a: object, b: object, *args) -> bool:
    return (less(a, b) or soft_equals(a, b)) and (not args or less_or_equal(b, *args))


OPERATIONS = {
    "==": soft_equals,
    "!=": lambda a, b: not soft_equals(a, b),
    ">": lambda a, b: less(b, a),
    ">=": lambda a, b: less(b, a) or soft_equals(a, b),
    "<": less,
    "<=": less_or_equal,
    "in": lambda a, b: a in b if "__contains__" in dir(b) else False,
    "not in": lambda a, b: not (a in b) if "__contains__" in dir(b) else True,
    "contains": lambda a, b: any(element in a for element in b) if "__contains__" in dir(b) else b in a,
}
